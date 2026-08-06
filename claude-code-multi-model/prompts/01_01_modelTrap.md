# 01_01: Build the TaskFlow Help Desk Chatbot

Build a single-model help desk chatbot with Claude Sonnet, with debug output for cost visibility.

## Claude Code Prompt

```
Build a command-line help desk chatbot in src/helpdesk_bot.py for TaskFlow,
a project management tool. Use Claude Sonnet via the Anthropic API.

System prompt with product tiers: Free (5 users, basic boards),
Pro ($12/user/month, unlimited projects, Gantt charts, Slack/GitHub/Jira
integrations, up to 50 users), Enterprise (custom pricing, SSO/SAML,
audit logs, dedicated support, unlimited). Tell the model to respond
in plain text only, no markdown formatting.

Color-coded terminal output: green bold for "You:" prompt, cyan bold
for "TaskFlow:" responses. Print a startup banner with the bot name
and model info. Conversation loop that exits on quit or exit.

Debug flag (--debug) that prints a dim gray line after each response
showing: model name, input tokens, output tokens, latency in seconds,
and estimated cost (Sonnet pricing: $3/M input, $15/M output).
Strip any ** markdown from responses before printing.
```

## What This Creates

`src/helpdesk_bot.py` — Single-model chatbot with colored output and cost debug mode. Run with `python src/helpdesk_bot.py --debug`.