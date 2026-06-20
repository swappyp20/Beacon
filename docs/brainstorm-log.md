# Beacon — Brainstorm & Decision Log

**Project:** Slack Agent Builder Challenge entry
**Date started:** 2026-06-15
**Track:** Slack Agent for Good
**Status:** Design in progress (architecture approved; safety model + tech stack pending)

---

## Hackathon context

The Slack Agent Builder Challenge asks builders to create an application that uses
**at least one** of these technologies and fits **at least one** track:

**Eligible technologies**
- Slack AI capabilities
- MCP server integration
- Real-Time Search (RTS) API

**Tracks**
- New Slack Agent
- **Slack Agent for Good** ← our track
- Slack Agent for Organizations

**Prizes:** share of $42,000 USD, Dreamforce 2026 trip, Slack swag, community gathering
invite, newsletter/social feature.

---

## Decisions made (in order)

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| 1 | Primary goal | **Social good / portfolio** | Strong narrative for judges; plays to builder's security/AI background. |
| 2 | Domain | **Youth-wellbeing navigator** (evolved from "nonprofit grant navigator") | Builder wanted to go beyond grants into holistic, kid-focused life support incl. mental health. |
| 3 | Primary user | **Youth-org staff** (mentors, coordinators) — NOT kids directly | Kids aren't on Slack; AI-to-minor mental-health advice is a legal/ethical minefield. Serving the adults who serve kids keeps a licensed human in every sensitive loop. |
| 4 | Org setting | **Youth mentoring nonprofit** (e.g., Big Brothers Big Sisters style) | "Whole life" support fits mentoring; humane demo without crisis-porn. |
| 5 | Scope level | **Full ops platform (C)** — designed in full, built behind a hard demo cut line | Builder wants the full vision; we de-risk with strict build priority so we don't ship four half-built pillars. |
| 6 | Architecture & tech mapping | **Approved** (see below) | — |
| 7 | Safety & privacy model | **Approved** | Human-in-loop guarantee, PII minimization, channel-scoped access, audit trail, crisis fast-path. Builder's security edge. |
| 8 | Agent runtime | **Bolt for Python** | Matches builder's Python/agent background; best MCP + Claude fit. |
| 9 | Resource discovery | **Curated directory via custom MCP** (web search = documented upgrade) | Reliable demo; reinforces "vetted/safe" story; in demo nothing leaves Slack. |
| 10 | Mentee scorecard | **Added as Pillar 6 — holistic, strengths-based, NO numbers/grades** | Builder's idea; reframed away from "scoring a child" to a supportive whole-child snapshot. |
| 11 | Scorecard generation | **Hybrid: agent drafts, mentor edits/approves → Canvas** | Showcases Slack AI + RTS; keeps a human in control of a sensitive artifact. |
| 12 | UI / frontend | **Slack-native only** (Block Kit, modals, Canvas, App Home) — NO separate web app | Slack *is* the UI; spec was missing a named presentation layer. Added §4.1. Reference mockup in `.superpowers/brainstorm/`. |
| 13 | Triage entry point | **Mentor-initiated, DM-first**; "triage message" is the agent's reply (step 6 of 8-step flow) | Most private for minor info; natural post-session moment. Agent never messages first. Documented 8-step flow in Pillar 1. |
| 14 | Mission clarity | **Reworded §1 to lead with "agent for the adults who serve kids, not the children"** + added "Actors at a glance" table | A stakeholder misread the mission as kid-facing — a judge could too. Mentee never interacts with the agent. |
| 15 | Last mile / "Share & log" | **Hand-off sheet + log** (option A): agent makes a plain-language hand-off the MENTOR delivers; never contacts child/family directly | Value reaches mentee via mentor (human bridge). Family-outreach drafting = documented upgrade. Resolves parked Pillar 2 question. |
| 16 | Hackathon build scope | **Hero + planned stretch** (office-hours review). Pillar 1 fully real; Pillar 2 + scorecard = scheduled stretch; cut 4/5/audit/roles to spoken story | Real rules: deadline 2026-07-13, judges RUN a sandbox, 4 equal criteria incl. UX ($2k prize). Depth+polish+working guardrail > broad-and-broken. Added spec §14. |
| 17 | MCP approach | **Build a custom Python MCP server** (Approach A) for org knowledge (protocols/resources) | Claims all 3 eligible techs + Best-Tech-Impl angle. Clarified: distinct from Slack's MCP server (which is for external agents); our first-party Bolt app uses native Slack API, so consuming Slack's MCP would be redundant. Fixed §2. |

---

## Key correction discovered during design

**Slack's Real-Time Search (RTS) API searches the org's OWN Slack workspace data —
not the public web.** This reshaped the design:

- "Find live external grants/scholarships" cannot use RTS.
- RTS is repurposed as **institutional memory** (search the org's own Slack: past
  mentee notes, prior similar situations, safeguarding decisions).
- External resource/grant discovery uses a **web-search tool**, with a **PII-redaction
  step before any off-platform call** (builder's security edge).

Sources:
- https://docs.slack.dev/ai/slack-mcp-server/
- https://docs.slack.dev/ai/developing-agents/
- https://docs.slack.dev/changelog/2026/02/17/slack-mcp/

---

## Technology mapping (approved)

- **Slack AI capabilities** → the agent itself: **Bolt (Python)** + `Assistant` class +
  Claude for reasoning; streaming responses, suggested prompts.
- **MCP server integration** → (a) a **custom MCP server** over the org's own knowledge
  (safeguarding protocols, vetted resource directory, past grant proposals);
  (b) optionally consume the **Slack MCP server** (canvases/messaging).
- **RTS API** → **institutional memory**: real-time search over the org's own Slack.
- **Web-search tool** (not RTS) → external resource/grant discovery, behind PII redaction.

---

## Architecture — "Beacon" (5 pillars)

The agent runs inside the mentoring nonprofit's Slack.

1. **Wellbeing triage & safeguarding** *(differentiator)* — mentor describes a concern →
   agent assesses urgency by a rubric (never diagnoses), surfaces the org's own escalation
   protocol (custom MCP), pulls relevant institutional memory (RTS), routes/@mentions the
   right human, logs a structured follow-up. **Human in every loop — agent never closes a
   safeguarding case itself.**
2. **Resource navigator** — mentor describes a mentee need → agent matches vetted resources
   (custom MCP directory + redacted web search), returns eligibility + how-to, logs what
   was shared.
3. **Follow-up & continuity tracking** — open items per mentee, proactive nudges, living
   per-mentee Canvas. Uses RTS to reconstruct history.
4. **Grant & funding support** *(original idea)* — finds grant calls (web), drafts with
   Slack AI, references past proposals (MCP), tracks deadlines.
5. **Mentor–mentee matching & impact reporting** — suggests matches; generates board
   impact reports (Slack AI over logged data + RTS).
6. **Mentee scorecard** — strengths-based, qualitative whole-child snapshot across 5 life
   domains (status: Thriving/Steady/Needs attention/Unknown — no numbers). Agent drafts
   from logged data + RTS; mentor approves; saved/versioned on the per-mentee Canvas.

### Demo cut line (de-risks "full vision")
- **Above the line — must work for demo:** Pillars **1 + 2** (showcases all 3 techs).
- **Then:** Pillar **3** (cheap, high operational credibility).
- **Upside:** Pillars **4 + 5 + 6** (Pillar 6 = most demo-friendly upside item).

---

## Open / pending design sections
- [x] Safety & privacy model (minor PII, audit trails, escalation guarantees, access control)
- [x] Concrete tech stack (Bolt Python, Claude, custom MCP, SQLite, Canvas; curated directory)
- [x] Final design spec → `docs/superpowers/specs/2026-06-15-beacon-design.md`
- [x] Clarification pass (5 Qs) → recorded in spec `## Clarifications` (Session 2026-06-15)
- [ ] User review of spec
- [ ] Implementation plan (via writing-plans skill)

## Clarification answers (2026-06-15)
1. Mentee PII: only pseudonymous handle + internal ID in SQLite; real PII stays in Slack.
2. RTS scope: mentee + safeguarding channels the agent belongs to (not whole workspace).
3. Roles/authZ: Slack user groups + channel membership (no separate roles store).
4. Triage rubric: from org's MCP protocol, with built-in default fallback.
5. Crisis detection: two-stage fail-safe (keyword OR LLM classifier), biased to false positives.
