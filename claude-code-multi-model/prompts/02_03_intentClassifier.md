# 02_03: Add Intent Classification with Claude Haiku

Add a fast, cheap classifier that runs before the main response.

## Claude Code Prompt

```
Modify src/helpdesk_bot.py to add an intent classifier using Claude Haiku
(claude-haiku-4-5-20251001) that runs before the main Sonnet response.

The classifier should:
- Send the user's message to Haiku with a prompt that says: classify
  this help desk message and return ONLY valid JSON with two fields:
  "intent" (one of: product_question, greeting, off_topic, complex,
  adversarial) and "confidence" (0.0 to 1.0).
- Parse the JSON response.
- In --debug mode, print a dim gray classification line showing:
  classifier model, intent, confidence, latency, and cost
  (Haiku: $1/M input, $5/M output) BEFORE the generation debug line.

Don't change the routing yet — still send everything to Sonnet after
classifying. We're adding classification first, routing next.
Strip any ** markdown from all responses before printing.
```

## What This Creates

Modified `src/helpdesk_bot.py` with a Haiku classification step that runs before every Sonnet response. Debug mode shows both the classification and generation costs.
