import json
import math
import os
import statistics

SESSION_LOG = os.path.join("logs", "session.jsonl")
FLAGGED_LOG = os.path.join("logs", "flagged_for_review.jsonl")

# ANSI colors
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
BOLD = "\033[1m"
DIM = "\033[2;37m"
RESET = "\033[0m"


def rag(value, green_below, amber_below):
    if value < green_below:
        return f"{GREEN}[GREEN]{RESET}"
    elif value < amber_below:
        return f"{YELLOW}[AMBER]{RESET}"
    else:
        return f"{RED}[RED]{RESET}"


def percentile(data, p):
    if not data:
        return 0.0
    s = sorted(data)
    k = (len(s) - 1) * (p / 100)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[f] * (c - k) + s[c] * (k - f)


def load_records(path):
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def cost_trend(records):
    if len(records) < 4:
        return "insufficient data"
    half = len(records) // 2
    first_half = [r["cost_total"] for r in records[:half]]
    second_half = [r["cost_total"] for r in records[half:]]
    mean_first = statistics.mean(first_half)
    mean_second = statistics.mean(second_half)
    if mean_second > mean_first * 1.1:
        return f"{RED}increasing{RESET}"
    elif mean_second < mean_first * 0.9:
        return f"{GREEN}decreasing{RESET}"
    else:
        return f"{GREEN}stable{RESET}"


def main():
    if not os.path.exists(SESSION_LOG):
        print(f"\nNo log file found at {SESSION_LOG}")
        print("Run the helpdesk bot first to generate logs:")
        print(f"  python src/helpdesk_bot.py --debug\n")
        return

    records = load_records(SESSION_LOG)
    total = len(records)
    if total == 0:
        print("\nLog file is empty. No messages to report.\n")
        return

    border = "=" * 70
    section = "-" * 70

    print(f"\n{BOLD}{border}")
    print(f"  SYSTEM HEALTH REPORT")
    print(f"{border}{RESET}")

    # Total messages
    print(f"\n{BOLD}  MESSAGES{RESET}")
    print(section)
    print(f"  Total processed:  {total}")

    # Route distribution
    print(f"\n{BOLD}  ROUTE DISTRIBUTION{RESET}")
    print(section)
    route_counts = {}
    for r in records:
        route = r["route"]
        route_counts[route] = route_counts.get(route, 0) + 1
    for route, count in sorted(route_counts.items()):
        pct = (count / total) * 100
        print(f"  {route:24s} {count:4d}  ({pct:5.1f}%)")

    # Cost
    costs = [r["cost_total"] for r in records]
    total_cost = sum(costs)
    mean_cost = total_cost / total
    cost_r = rag(mean_cost, 0.005, 0.01)
    print(f"\n{BOLD}  COST{RESET}")
    print(section)
    print(f"  Total:            ${total_cost:.6f}")
    print(f"  Mean per message: ${mean_cost:.6f} {cost_r}")
    print(f"  Trend:            {cost_trend(records)}")

    # Latency
    guardrail_times = [r["latency_guardrail_ms"] for r in records if r["latency_guardrail_ms"] is not None]
    classify_times = [r["latency_classify_ms"] for r in records if r["latency_classify_ms"] is not None]
    sonnet_times = [r["latency_sonnet_ms"] for r in records if r["latency_sonnet_ms"] is not None]
    total_times = [r["latency_total_ms"] for r in records if r["latency_total_ms"] is not None]

    print(f"\n{BOLD}  LATENCY{RESET}")
    print(section)

    def latency_row(label, values, g, a):
        if not values:
            print(f"  {label:18s} (no data)")
            return
        m = statistics.mean(values)
        p95 = percentile(values, 95)
        r = rag(p95, g, a)
        print(f"  {label:18s} mean={m:8.2f}ms  P95={p95:8.2f}ms {r}")

    latency_row("Guardrail", guardrail_times, 10, 50)
    latency_row("Classification", classify_times, 500, 1000)
    latency_row("Sonnet", sonnet_times, 3000, 5000)
    latency_row("Total", total_times, 3500, 6000)

    # Safety
    blocked_count = sum(1 for r in records if r["was_blocked"])
    pii_count = sum(1 for r in records if r["pii_found"])
    blocked_r = rag(blocked_count, 1, 5)
    pii_r = rag(pii_count, 1, 5)
    print(f"\n{BOLD}  SAFETY{RESET}")
    print(section)
    print(f"  Attacks blocked:    {blocked_count} {blocked_r}")
    print(f"  PII redacted:       {pii_count} {pii_r}")

    # Reliability
    fallback_count = sum(1 for r in records if r["was_fallback"])
    fallback_pct = (fallback_count / total) * 100
    fallback_r = rag(fallback_pct, 5, 15)

    flagged_count = 0
    if os.path.exists(FLAGGED_LOG):
        flagged_count = len(load_records(FLAGGED_LOG))
    flagged_pct = (flagged_count / total) * 100
    flagged_r = rag(flagged_pct, 5, 15)

    print(f"\n{BOLD}  RELIABILITY{RESET}")
    print(section)
    print(f"  Fallback rate:      {fallback_pct:5.1f}% ({fallback_count}/{total}) {fallback_r}")
    print(f"  Flagged for review: {flagged_pct:5.1f}% ({flagged_count}/{total}) {flagged_r}")

    print(f"\n{BOLD}{border}{RESET}\n")


if __name__ == "__main__":
    main()
