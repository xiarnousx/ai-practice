import re
import sys
import time

import anthropic

from helpdesk_bot import SYSTEM_PROMPT

# Models and their pricing (per million tokens)
MODELS = [
    {
        "id": "claude-haiku-4-5-20251001",
        "name": "Haiku",
        "input_cost": 1.0,
        "output_cost": 5.0,
    },
    {
        "id": "claude-sonnet-4-20250514",
        "name": "Sonnet",
        "input_cost": 3.0,
        "output_cost": 15.0,
    },
    {
        "id": "claude-opus-4-20250514",
        "name": "Opus",
        "input_cost": 15.0,
        "output_cost": 75.0,
    },
]

# ANSI color codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def estimate_cost(input_tokens: int, output_tokens: int, model: dict) -> float:
    return (input_tokens / 1_000_000 * model["input_cost"]) + (
        output_tokens / 1_000_000 * model["output_cost"]
    )


def render_markdown_bold(text: str) -> str:
    return re.sub(r'\*\*(.+?)\*\*', f'{BOLD}\\1{RESET}', text)


def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} \"Your message here\"")
        sys.exit(1)

    message = sys.argv[1]
    client = anthropic.Anthropic()
    results = []

    print(f"\n{CYAN}{BOLD}Comparing 3 Claude models{RESET}")
    print(f"{DIM}Message: \"{message}\"{RESET}\n")

    for model in MODELS:
        print(f"  Querying {model['name']:<8} ... ", end="", flush=True)

        start = time.time()
        response = client.messages.create(
            model=model["id"],
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": message}],
        )
        latency = time.time() - start

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost = estimate_cost(input_tokens, output_tokens, model)
        text = response.content[0].text

        results.append({
            "name": model["name"],
            "model_id": model["id"],
            "latency": latency,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
            "response": text,
        })
        print(f"{latency:.2f}s")

    # Find min/max cost for coloring
    costs = [r["cost"] for r in results]
    min_cost = min(costs)
    max_cost = max(costs)

    def color_for_cost(cost: float) -> str:
        if cost == min_cost:
            return GREEN
        elif cost == max_cost:
            return RED
        return YELLOW

    # --- Comparison Table ---
    print(f"\n{CYAN}{BOLD}{'='*90}")
    print(f"  MODEL COMPARISON")
    print(f"{'='*90}{RESET}\n")

    header = f"  {'Model':<10} {'Latency':>8} {'In':>6} {'Out':>6} {'Cost':>12} {'Response Preview'}"
    print(header)
    print(f"  {'-'*86}")

    for r in results:
        color = color_for_cost(r["cost"])
        preview = render_markdown_bold(r["response"].replace("\n", " ")[:150])
        print(
            f"  {BOLD}{r['name']:<10}{RESET} {r['latency']:>7.2f}s {r['input_tokens']:>6} "
            f"{r['output_tokens']:>6} {color}${r['cost']:>10.6f}{RESET}  "
            f"{DIM}{preview}{RESET}"
        )

    # --- Cost multipliers ---
    print(f"\n  {CYAN}{BOLD}Cost multipliers vs cheapest:{RESET}")
    for r in results:
        multiplier = r["cost"] / min_cost if min_cost > 0 else 0
        color = color_for_cost(r["cost"])
        print(f"    {r['name']:<10} {color}{multiplier:>6.1f}x{RESET}")

    # --- Full Responses ---
    print(f"\n{CYAN}{BOLD}{'='*90}")
    print(f"  FULL RESPONSES")
    print(f"{'='*90}{RESET}\n")

    for r in results:
        print(f"  {CYAN}{BOLD}--- {r['name']} ---{RESET}")
        print(f"  {DIM}({r['model_id']}){RESET}\n")
        print(render_markdown_bold(r["response"]))
        print()


if __name__ == "__main__":
    main()
