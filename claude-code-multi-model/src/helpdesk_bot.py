import argparse
import json
import math
import os
import re
import statistics
import time
import uuid
from datetime import datetime, timezone

import anthropic

MODEL = "claude-sonnet-4-6"
CLASSIFIER_MODEL = "claude-haiku-4-5-20251001"

CLASSIFIER_PROMPT = """Classify this help desk message and return ONLY valid JSON with two fields:
"intent" (one of: product_question, greeting, off_topic, complex, adversarial)
"confidence" (0.0 to 1.0)"""

CANNED_RESPONSES = {
    "greeting": "Hi there! How can I help you with TaskFlow today?",
    "off_topic": "I can only help with TaskFlow questions. For other inquiries, contact support@taskflow.com",
    "adversarial": "I'm not able to help with that request.",
}

SYSTEM_PROMPT = """You are a helpful support agent for TaskFlow, a project management tool.

TaskFlow offers three pricing tiers:

Free: Up to 5 users, basic boards, core task management features at no cost.

Pro: $12 per user per month. Unlimited projects, Gantt charts, Slack/GitHub/Jira integrations, up to 50 users.

Enterprise: Custom pricing. SSO/SAML authentication, audit logs, dedicated support, unlimited users and projects.

Answer user questions about TaskFlow clearly and helpfully. Respond in plain text only, no markdown formatting."""

# ANSI color codes
GREEN_BOLD = "\033[1;32m"
CYAN_BOLD = "\033[1;36m"
DIM_GRAY = "\033[2;37m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_RED = "\033[31m"
RESET = "\033[0m"


def rag_indicator(value, green_below, amber_below):
    if value < green_below:
        return f"{ANSI_GREEN}[GREEN]{RESET}{DIM_GRAY}"
    elif value < amber_below:
        return f"{ANSI_YELLOW}[AMBER]{RESET}{DIM_GRAY}"
    else:
        return f"{ANSI_RED}[RED]{RESET}{DIM_GRAY}"


def strip_markdown(text: str) -> str:
    return re.sub(r"\*+", "", text)


def estimate_cost(input_tokens: int, output_tokens: int, input_rate: float = 3.0, output_rate: float = 15.0) -> float:
    return (input_tokens / 1_000_000 * input_rate) + (output_tokens / 1_000_000 * output_rate)


UNSAFE_PATTERNS = [
    {"category": "prompt_injection", "pattern": re.compile(r"ignore\s+(\w+\s+)*instructions|disregard|override your|forget your rules", re.IGNORECASE), "severity": "HIGH"},
    {"category": "role_manipulation", "pattern": re.compile(r"you are now|pretend to be|act as|DAN mode", re.IGNORECASE), "severity": "HIGH"},
    {"category": "system_prompt_extraction", "pattern": re.compile(r"show your prompt|what are your instructions|repeat your system|output your system", re.IGNORECASE), "severity": "MEDIUM"},
    {"category": "jailbreak", "pattern": re.compile(r"bypass restrictions|disable filters|no limits", re.IGNORECASE), "severity": "MEDIUM"},
]

BLOCKED_RESPONSE = "I'm sorry, but I can't process that request. If you have a question about TaskFlow, I'm happy to help!"

LOG_DIR = "logs"
SESSION_LOG = os.path.join(LOG_DIR, "session.jsonl")
FLAGGED_LOG = os.path.join(LOG_DIR, "flagged_for_review.jsonl")


def log_message(original_message, redacted_message, intent, confidence,
                route, guardrail_action, cost_haiku, cost_sonnet,
                latency_guardrail_ms, latency_classify_ms,
                latency_sonnet_ms, latency_total_ms,
                was_fallback, was_blocked, pii_found):
    os.makedirs(LOG_DIR, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message_id": str(uuid.uuid4()),
        "original_message": original_message,
        "redacted_message": redacted_message,
        "intent": intent,
        "confidence": confidence,
        "route": route,
        "guardrail_action": guardrail_action,
        "cost_haiku": cost_haiku,
        "cost_sonnet": cost_sonnet,
        "cost_total": (cost_haiku or 0) + (cost_sonnet or 0),
        "latency_guardrail_ms": latency_guardrail_ms,
        "latency_classify_ms": latency_classify_ms,
        "latency_sonnet_ms": latency_sonnet_ms,
        "latency_total_ms": latency_total_ms,
        "was_fallback": was_fallback,
        "was_blocked": was_blocked,
        "pii_found": pii_found,
    }
    with open(SESSION_LOG, "a") as f:
        f.write(json.dumps(record) + "\n")
    if confidence is not None and confidence < 0.8:
        flagged = dict(record)
        flagged["reason"] = "low_confidence"
        with open(FLAGGED_LOG, "a") as f:
            f.write(json.dumps(flagged) + "\n")

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN = re.compile(
    r"\+?1?\s?[\s.-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}"
)


def detect_pii(message: str, debug: bool):
    start = time.time()
    redacted = message
    pii_count = 0

    emails = EMAIL_PATTERN.findall(redacted)
    pii_count += len(emails)
    redacted = EMAIL_PATTERN.sub("[EMAIL REDACTED]", redacted)

    phones = PHONE_PATTERN.findall(redacted)
    pii_count += len(phones)
    redacted = PHONE_PATTERN.sub("[PHONE REDACTED]", redacted)

    latency_ms = (time.time() - start) * 1000

    if debug:
        result = "PII detected" if pii_count > 0 else "clean"
        print(
            f"{DIM_GRAY}[guardrail] PII Detection | result={result} | "
            f"items={pii_count} | time={latency_ms:.1f}ms{RESET}"
        )

    return redacted, pii_count, latency_ms


def detect_unsafe(message: str, debug: bool):
    start = time.time()
    matches = []

    for rule in UNSAFE_PATTERNS:
        if rule["pattern"].search(message):
            matches.append({"category": rule["category"], "severity": rule["severity"]})

    high_count = sum(1 for m in matches if m["severity"] == "HIGH")
    medium_count = sum(1 for m in matches if m["severity"] == "MEDIUM")
    blocked = high_count > 0 or medium_count >= 2

    latency_ms = (time.time() - start) * 1000

    if debug:
        if matches:
            matched_str = ", ".join(f"{m['category']}({m['severity']})" for m in matches)
        else:
            matched_str = "none"
        print(
            f"{DIM_GRAY}[guardrail] Unsafe Detection | matches={matched_str} | "
            f"blocked={blocked} | time={latency_ms:.1f}ms{RESET}"
        )

    return blocked, latency_ms


def classify_intent(client, user_message: str, debug: bool):
    start = time.time()
    response = client.messages.create(
        model=CLASSIFIER_MODEL,
        max_tokens=128,
        system=CLASSIFIER_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    latency = time.time() - start

    raw = response.content[0].text.strip()
    json_match = re.search(r"\{.*\}", raw, re.DOTALL)
    if json_match:
        raw = json_match.group()
    try:
        classification = json.loads(raw)
    except json.JSONDecodeError:
        classification = {"intent": "unknown", "confidence": 0.0}

    confidence = classification.get("confidence", 0.0)
    intent = classification["intent"]

    if confidence < 0.7:
        route = "fallback→sonnet"
    elif intent in CANNED_RESPONSES:
        route = "canned"
    else:
        route = "classified→sonnet"

    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    haiku_cost = estimate_cost(input_tokens, output_tokens, input_rate=1.0, output_rate=5.0)

    if debug:
        print(
            f"{DIM_GRAY}[classifier] model={CLASSIFIER_MODEL} | "
            f"intent={classification['intent']} | confidence={classification['confidence']} | "
            f"route={route} | latency={latency:.2f}s | cost=${haiku_cost:.6f}{RESET}"
        )

    classification["route"] = route
    classification["_metrics"] = {
        "latency_ms": latency * 1000,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost": haiku_cost,
    }
    return classification


def percentile(data, p):
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * (p / 100)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_data[int(k)]
    return sorted_data[f] * (c - k) + sorted_data[c] * (k - f)


def latency_stats(values, label, green_below, amber_below):
    if not values:
        return f"  {label:18s} (no data)"
    mean = statistics.mean(values)
    med = statistics.median(values)
    p95 = percentile(values, 95)
    p99 = percentile(values, 99)
    rag = rag_indicator(p95, green_below, amber_below)
    return (
        f"  {label:18s} mean={mean:8.2f}ms | median={med:8.2f}ms | "
        f"P95={p95:8.2f}ms | P99={p99:8.2f}ms {rag}"
    )


def print_report(message_metrics):
    total = len(message_metrics)
    if total == 0:
        print(f"\n{DIM_GRAY}No messages to report.{RESET}")
        return

    border = "=" * 70
    section = "-" * 70

    # Route distribution
    route_counts = {}
    for m in message_metrics:
        r = m["route"]
        route_counts[r] = route_counts.get(r, 0) + 1

    # Latency lists
    guardrail_times = [m["guardrail_ms"] for m in message_metrics]
    classify_times = [m["classify_ms"] for m in message_metrics if m["classify_ms"] is not None]
    sonnet_times = [m["sonnet_ms"] for m in message_metrics if m["sonnet_ms"] is not None]
    total_times = [m["total_ms"] for m in message_metrics]

    # Cost
    total_haiku_cost = sum(m["haiku_cost"] for m in message_metrics if m["haiku_cost"] is not None)
    total_sonnet_cost = sum(m["sonnet_cost"] for m in message_metrics if m["sonnet_cost"] is not None)
    total_cost = total_haiku_cost + total_sonnet_cost
    mean_cost = total_cost / total

    # Safety
    blocked_count = sum(1 for m in message_metrics if m["blocked"])
    pii_total = sum(m["pii_count"] for m in message_metrics)

    # Reliability
    fallback_count = sum(1 for m in message_metrics if m["route"] == "fallback\u2192sonnet")
    fallback_pct = (fallback_count / total) * 100
    confidences = [m["confidence"] for m in message_metrics if m["confidence"] is not None]
    avg_confidence = statistics.mean(confidences) if confidences else 0.0

    print(f"\n{DIM_GRAY}{border}")
    print(f"  EVALUATION REPORT")
    print(f"{border}")

    # Summary
    print(f"{section}")
    print(f"  SUMMARY")
    print(f"{section}")
    print(f"  Total messages:   {total}")

    # Route distribution
    print(f"{section}")
    print(f"  ROUTE DISTRIBUTION")
    print(f"{section}")
    for route, count in sorted(route_counts.items()):
        pct = (count / total) * 100
        print(f"  {route:24s} {count:4d}  ({pct:5.1f}%)")

    # Latency
    print(f"{section}")
    print(f"  LATENCY")
    print(f"{section}")
    print(latency_stats(guardrail_times, "Guardrail", 10, 50))
    print(latency_stats(classify_times, "Classification", 500, 1000))
    print(latency_stats(sonnet_times, "Sonnet", 3000, 5000))
    print(latency_stats(total_times, "Total", 3500, 6000))

    # Cost
    cost_rag = rag_indicator(mean_cost, 0.005, 0.01)
    print(f"{section}")
    print(f"  COST")
    print(f"{section}")
    print(f"  Total cost:       ${total_cost:.6f}")
    print(f"  Mean per message: ${mean_cost:.6f} {cost_rag}")
    print(f"  Haiku total:      ${total_haiku_cost:.6f}")
    print(f"  Sonnet total:     ${total_sonnet_cost:.6f}")

    # Safety
    print(f"{section}")
    print(f"  SAFETY")
    print(f"{section}")
    print(f"  Attacks blocked:  {blocked_count}")
    print(f"  PII items redacted: {pii_total}")

    # Reliability
    fallback_rag = rag_indicator(fallback_pct, 2, 5)
    print(f"{section}")
    print(f"  RELIABILITY")
    print(f"{section}")
    print(f"  Fallback rate:    {fallback_pct:.1f}% {fallback_rag}")
    print(f"  Avg confidence:   {avg_confidence:.3f}")

    print(f"{border}{RESET}\n")


def print_banner():
    print(f"\n{'='*50}")
    print(f"  TaskFlow Help Desk")
    print(f"  Model: {MODEL}")
    print(f"  Classifier: {CLASSIFIER_MODEL}")
    print(f"{'='*50}")
    print("Type 'quit' or 'exit' to leave.\n")


def main():
    parser = argparse.ArgumentParser(description="TaskFlow Help Desk Chatbot")
    parser.add_argument("--debug", action="store_true", help="Show debug info after each response")
    parser.add_argument("--metrics", action="store_true", help="Show per-message metrics summary")
    parser.add_argument("--metrics-report", action="store_true", help="Show summary report on exit")
    args = parser.parse_args()

    client = anthropic.Anthropic()
    conversation_history = []
    total_messages = 0
    fallback_count = 0
    message_metrics = []

    print_banner()

    try:
        while True:
            print(f"{GREEN_BOLD}You:{RESET} ", end="")
            user_input = input().strip()

            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit"):
                print("Goodbye!")
                break

            total_start = time.time()

            redacted_input, pii_count, pii_latency_ms = detect_pii(user_input, args.debug)
            blocked, unsafe_latency_ms = detect_unsafe(user_input, args.debug)
            guardrail_ms = pii_latency_ms + unsafe_latency_ms

            if blocked:
                total_ms = (time.time() - total_start) * 1000
                total_messages += 1
                print(f"{CYAN_BOLD}TaskFlow:{RESET} {BLOCKED_RESPONSE}\n")
                message_metrics.append({
                    "route": "guardrail_block",
                    "guardrail_ms": guardrail_ms,
                    "classify_ms": None,
                    "sonnet_ms": None,
                    "total_ms": total_ms,
                    "haiku_cost": None,
                    "sonnet_cost": None,
                    "confidence": None,
                    "blocked": True,
                    "pii_count": pii_count,
                })
                log_message(
                    original_message=user_input,
                    redacted_message=redacted_input if pii_count > 0 else None,
                    intent=None,
                    confidence=None,
                    route="guardrail_block",
                    guardrail_action="blocked",
                    cost_haiku=None,
                    cost_sonnet=None,
                    latency_guardrail_ms=guardrail_ms,
                    latency_classify_ms=None,
                    latency_sonnet_ms=None,
                    latency_total_ms=total_ms,
                    was_fallback=False,
                    was_blocked=True,
                    pii_found=pii_count > 0,
                )
                if args.metrics:
                    guardrail_rag = rag_indicator(guardrail_ms, 10, 50)
                    print(f"{DIM_GRAY}[METRICS]")
                    print(f"  Route:      guardrail_block")
                    print(f"  Timing:     guardrail={guardrail_ms:.2f}ms {guardrail_rag} | total={total_ms:.2f}ms")
                    fallback_pct = (fallback_count / total_messages) * 100
                    print(f"  Fallback:   {fallback_pct:.1f}% {rag_indicator(fallback_pct, 2, 5)}")
                    print(f"{RESET}")
                conversation_history.append({"role": "user", "content": user_input})
                conversation_history.append({"role": "assistant", "content": BLOCKED_RESPONSE})
                continue

            if pii_count > 0:
                print(f"{CYAN_BOLD}[Privacy] Personal information detected and redacted for your protection.{RESET}")
                user_input = redacted_input

            conversation_history.append({"role": "user", "content": user_input})

            classification = classify_intent(client, user_input, args.debug)
            route = classification["route"]
            haiku_metrics = classification["_metrics"]

            sonnet_metrics = None

            if route == "canned":
                assistant_text = CANNED_RESPONSES[classification["intent"]]
                metrics_route = "canned_response"
            else:
                metrics_route = route
                start = time.time()
                response = client.messages.create(
                    model=MODEL,
                    max_tokens=1024,
                    system=SYSTEM_PROMPT,
                    messages=conversation_history,
                )
                latency = time.time() - start

                assistant_text = strip_markdown(response.content[0].text)

                sonnet_in = response.usage.input_tokens
                sonnet_out = response.usage.output_tokens
                sonnet_cost = estimate_cost(sonnet_in, sonnet_out)
                sonnet_metrics = {
                    "latency_ms": latency * 1000,
                    "input_tokens": sonnet_in,
                    "output_tokens": sonnet_out,
                    "cost": sonnet_cost,
                }

                if args.debug:
                    print(
                        f"{DIM_GRAY}[generation] model={response.model} | "
                        f"in={sonnet_in} | out={sonnet_out} | "
                        f"latency={latency:.2f}s | cost=${sonnet_cost:.6f}{RESET}\n"
                    )

            conversation_history.append({"role": "assistant", "content": assistant_text})
            total_messages += 1
            if metrics_route == "fallback\u2192sonnet":
                fallback_count += 1

            total_ms = (time.time() - total_start) * 1000
            message_metrics.append({
                "route": metrics_route,
                "guardrail_ms": guardrail_ms,
                "classify_ms": haiku_metrics["latency_ms"],
                "sonnet_ms": sonnet_metrics["latency_ms"] if sonnet_metrics else None,
                "total_ms": total_ms,
                "haiku_cost": haiku_metrics["cost"],
                "sonnet_cost": sonnet_metrics["cost"] if sonnet_metrics else None,
                "confidence": classification.get("confidence", 0.0),
                "blocked": False,
                "pii_count": pii_count,
            })
            log_message(
                original_message=user_input,
                redacted_message=redacted_input if pii_count > 0 else None,
                intent=classification.get("intent"),
                confidence=classification.get("confidence", 0.0),
                route=metrics_route,
                guardrail_action="passed",
                cost_haiku=haiku_metrics["cost"],
                cost_sonnet=sonnet_metrics["cost"] if sonnet_metrics else None,
                latency_guardrail_ms=guardrail_ms,
                latency_classify_ms=haiku_metrics["latency_ms"],
                latency_sonnet_ms=sonnet_metrics["latency_ms"] if sonnet_metrics else None,
                latency_total_ms=total_ms,
                was_fallback=metrics_route == "fallback→sonnet",
                was_blocked=False,
                pii_found=pii_count > 0,
            )

            print(f"{CYAN_BOLD}TaskFlow:{RESET} {assistant_text}\n")

            if args.metrics:
                total_cost = haiku_metrics["cost"] + (sonnet_metrics["cost"] if sonnet_metrics else 0.0)
                confidence = classification.get("confidence", 0.0)

                guardrail_rag = rag_indicator(guardrail_ms, 10, 50)
                classify_rag = rag_indicator(haiku_metrics["latency_ms"], 500, 1000)
                cost_rag = rag_indicator(total_cost, 0.005, 0.01)

                print(f"{DIM_GRAY}[METRICS]")
                print(f"  Route:      {metrics_route}")

                timing_parts = [f"guardrail={guardrail_ms:.2f}ms {guardrail_rag}", f"classification={haiku_metrics['latency_ms']:.2f}ms {classify_rag}"]
                if sonnet_metrics:
                    sonnet_rag = rag_indicator(sonnet_metrics["latency_ms"], 3000, 5000)
                    timing_parts.append(f"sonnet={sonnet_metrics['latency_ms']:.2f}ms {sonnet_rag}")
                timing_parts.append(f"total={total_ms:.2f}ms")
                print(f"  Timing:     {' | '.join(timing_parts)}")

                tokens_parts = [f"Haiku in={haiku_metrics['input_tokens']} out={haiku_metrics['output_tokens']}"]
                if sonnet_metrics:
                    tokens_parts.append(f"Sonnet in={sonnet_metrics['input_tokens']} out={sonnet_metrics['output_tokens']}")
                print(f"  Tokens:     {' | '.join(tokens_parts)}")

                cost_parts = [f"Haiku=${haiku_metrics['cost']:.6f}"]
                if sonnet_metrics:
                    cost_parts.append(f"Sonnet=${sonnet_metrics['cost']:.6f}")
                cost_parts.append(f"total=${total_cost:.6f} {cost_rag}")
                print(f"  Cost:       {' | '.join(cost_parts)}")

                print(f"  Confidence: {confidence}")

                fallback_pct = (fallback_count / total_messages) * 100
                print(f"  Fallback:   {fallback_pct:.1f}% {rag_indicator(fallback_pct, 2, 5)}")
                print(f"{RESET}")

    except KeyboardInterrupt:
        print("\nGoodbye!")

    if args.metrics_report and message_metrics:
        print_report(message_metrics)


if __name__ == "__main__":
    main()
