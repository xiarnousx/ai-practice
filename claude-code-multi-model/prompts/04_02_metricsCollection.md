# 04_02: Build Metrics Collection

Add timing, token tracking, and route recording to every message.

## Claude Code Prompt

```
Modify src/helpdesk_bot.py to add metrics collection. Add a --metrics
flag that prints a per-message metrics summary after each response.

Track for every message:
- Route taken: guardrail_block, canned_response, classified→sonnet,
  fallback→sonnet
- Timing per stage in milliseconds: guardrail, classification, sonnet
  (if called), total
- Token counts: Haiku input/output, Sonnet input/output (if called)
- Cost breakdown: Haiku cost, Sonnet cost (if called), total cost
- Confidence score from classifier (if called)

Print a [METRICS] block after each response showing all of the above.
Use dim gray text. Format timing as milliseconds with 2 decimal places.
Format cost as dollars with 6 decimal places.

The --metrics flag should work alongside --debug. When both are used,
show debug lines first, then the metrics summary.
```

## What This Creates

Modified `src/helpdesk_bot.py` with per-message metrics tracking. Run with `python src/helpdesk_bot.py --debug --metrics` to see both debug and metrics output.
