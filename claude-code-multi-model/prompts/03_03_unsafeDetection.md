# 03_03: Add Unsafe Request Detection

Add pattern matching that blocks prompt injections, jailbreaks, and role manipulation before any API call.

## Claude Code Prompt

```
Modify src/helpdesk_bot.py to add unsafe request detection as part
of the guardrails layer, running BEFORE any API call.

Detect these categories with regex/keyword matching:
- Prompt injection: "ignore previous instructions", "disregard",
  "override your", "forget your rules"
- Role manipulation: "you are now", "pretend to be", "act as",
  "DAN mode"
- System prompt extraction: "show your prompt", "what are your
  instructions", "repeat your system"
- Jailbreak: "bypass restrictions", "disable filters", "no limits"

Each pattern has a severity: HIGH or MEDIUM.
Blocking logic: block if any HIGH severity match OR 2+ MEDIUM matches.

If blocked: return a polite refusal immediately. No Haiku call,
no Sonnet call, no API cost. Print the refusal in cyan.

If both PII and unsafe detected: BLOCK takes priority over REDACT.

In --debug mode, show: patterns matched, severity levels, block
decision, and processing time in milliseconds. When blocked, do NOT
show classification or generation debug lines since no API was called.
```

## What This Creates

Modified `src/helpdesk_bot.py` with unsafe request detection. Prompt injections and jailbreak attempts are blocked in <1ms for $0 — no model ever sees them.
