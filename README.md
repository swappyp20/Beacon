# Beacon

> A guiding light and a signal when something needs attention.

**A Slack Agent for Good for the adults who serve kids.** Built for the Slack Agent Builder Challenge (track: *Slack Agent for Good*).

---

## Overview

Beacon is a Slack agent that helps the staff and volunteer mentors at a youth-mentoring nonprofit respond faster and more completely when a young person is struggling. A mentor describes a concern in plain language; Beacon triages it, grounds it in the organization's *own* safeguarding protocol, recalls what the team already knows about that mentee, routes it to the right human, and surfaces vetted resources.

Beacon serves the **adults who serve kids** — mentors, coordinators, and safeguarding leads. It is **not** a chatbot for children.

| Actor | On Slack? | Role |
|---|---|---|
| Mentor | Yes | Talks to Beacon about a mentee (the primary user) |
| Coordinator / safeguarding lead | Yes | Receives escalations; owns sensitive decisions |
| Mentee (a child) | **No** | The *subject* of the conversation, never a participant |

---

## The Problem

Youth-mentoring nonprofits run on the goodwill of stretched-thin staff and volunteer mentors. When a mentee is struggling — emotionally, academically, or with basic needs — the mentor's right response depends on three things that are usually scattered and slow to reach:

1. **The org's protocol** — what is the agreed step when a kid shows a wellbeing signal? It lives in a handbook nobody has open at 9pm after a session.
2. **The mentee's history** — has this come up before? What did the team decide last time? It is buried across months of notes.
3. **The right resource** — a fee waiver, a tutor, a crisis line. Finding the vetted one takes time the mentor doesn't have.

So concerns live in one mentor's head, follow-ups slip, and **kids fall through the cracks**. The hardest cases are also the most sensitive, where a wrong or delayed move carries real weight.

---

## The Solution

Beacon is the mentor's co-pilot inside Slack. A mentor sends a message like:

> *"Met Maya today — she's stressed about college application fees and seemed really down."*

Beacon then, in one reply:

- **Checks for crisis first.** A fail-safe guardrail (keyword *or* LLM, biased toward catching) scans for imminent harm. If found, it short-circuits everything and surfaces the crisis protocol plus the on-call human immediately — with a clear *"I am not a crisis service"* disclaimer.
- **Assesses urgency** against the organization's own rubric (`routine / elevated / urgent / crisis`). It never diagnoses.
- **Grounds the response in the org's protocol**, pulled live from a custom knowledge server (MCP).
- **Recalls institutional memory** — prior notes on this mentee and similar past situations — using Slack's Real-Time Search over the team's own channels.
- **Routes to a human.** One click posts a structured summary to `#safeguarding-leads`. A human owns every sensitive decision; Beacon never closes a case.
- **Logs a follow-up** so nothing is dropped, and writes an audit trail.

Beyond triage, Beacon also surfaces **vetted resources** matched to a stated need (with a plain-language hand-off the mentor gives the family), and can draft a **strengths-based progress snapshot** for a mentee that the mentor reviews and approves to a Slack Canvas — no scores, no grades, just a whole-child view.

The whole interface is Slack itself: Block Kit messages, Canvas, and an App Home dashboard. There is no separate web app to learn.

---

## Safety and trust (the heart of it)

Because Beacon touches the wellbeing of minors, the safety posture is the product, not an add-on:

- **Human in every sensitive loop.** Beacon assesses, surfaces protocol, and routes — it never diagnoses, counsels, or closes a case.
- **It never talks to a child.** Value reaches the mentee through the mentor, never from the agent directly.
- **Crisis fast-path** that fails safe (false positives are acceptable; misses are not).
- **Minimal data on minors.** Only a pseudonymous handle is stored outside Slack; identifying details stay in the channels the org already controls.
- **An audit trail** for every escalation, resource shared, and follow-up.

---

## Built on

Beacon uses all three eligible Slack technologies:

- **Slack AI capabilities** — the agent itself (Bolt for Python + the `Assistant` API + Claude), with streamed responses and Block Kit.
- **MCP server integration** — a custom Model Context Protocol server exposing the org's safeguarding protocols and vetted resource directory.
- **Real-Time Search (RTS) API** — institutional memory over the org's own Slack channels.

**Stack:** Python · `slack-bolt` · Claude (`claude-opus-4-8` + `claude-haiku-4-5`) · a custom Python MCP server · SQLite · Slack Block Kit / Canvas / App Home.

---

## Status

In active development for the Slack Agent Builder Challenge (deadline 2026-07-13). The build is sequenced as a hero flow (wellbeing triage) made fully real, then a planned stretch (resource navigator + mentee scorecard).

- Design spec: [`docs/superpowers/specs/2026-06-15-beacon-design.md`](docs/superpowers/specs/2026-06-15-beacon-design.md)
- Implementation plan: [`docs/superpowers/plans/2026-06-20-beacon.md`](docs/superpowers/plans/2026-06-20-beacon.md)
- Decision log: [`docs/brainstorm-log.md`](docs/brainstorm-log.md)

## Running it (dev sandbox)

> Full steps and the demo runbook land with the implementation. In short:

1. `pip install -e ".[dev]"`
2. Copy `.env.example` to `.env` and fill the Slack (bot + app) and Anthropic tokens.
3. Seed the BrightPath sandbox, then run `python -m beacon.app` and DM the app a mentee concern.

## License

See [LICENSE](LICENSE).
