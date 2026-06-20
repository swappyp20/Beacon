# Beacon Demo Runbook

## One-time sandbox setup
1. Create a Slack app in a dev workspace; enable Socket Mode.
2. Add bot scopes: `chat:write`, `channels:manage`, `channels:read`, `search:read`,
   `assistant:write`, `canvases:write`. Install to the workspace.
3. Copy `.env.example` to `.env`; fill `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`, `ANTHROPIC_API_KEY`.
4. `python seed/seed_sandbox.py` → paste the printed `RTS_SCOPE_CHANNELS` into `.env`.
5. `python -m beacon.app`
6. Invite `slackhack@salesforce.com` and `testing@devpost.com` to the workspace (submission requirement).

## 5 pre-record tests (all must pass before recording)
1. **Crisis eval:** `python evals/run_crisis_eval.py` → "PASS: all 10 crisis cases fired."
2. **Golden path:** DM "Met Maya today, stressed about college fees, seemed really down."
   → triage card (Elevated) + MCP protocol line + ≥1 RTS Maya memory hit + working Route button.
3. **Unknown mentee:** DM "a kid I met seemed off" → agent asks which mentee, invents nothing.
4. **MCP-down fallback:** stop the MCP server, DM a concern → agent still triages on the
   default rubric and notes the protocol is unavailable; no crash.
5. **RTS dry-run:** DM about Jordan → a Jordan memory hit appears (proves scoped RTS works).

## ~3-minute video script (spec §14)
- 0:00 Problem: stretched mentors, kids fall through cracks.
- 0:20 Maya triage: card with urgency + MCP protocol + RTS past note → route to #safeguarding-leads.
- 1:20 Resources: vetted matches + "Get hand-off sheet".
- 2:00 Scorecard Canvas closer (strengths-first, no numbers).
- 2:40 Ethics: never talks to kids, human in every loop. Close.

## Unit tests
`python -m pytest -q` (27 tests). The crisis eval (`run_crisis_eval.py`) is the live,
LLM-backed safety check and is separate.
