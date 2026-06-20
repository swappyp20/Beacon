# MentorOps — Design Spec

**Slack Agent Builder Challenge · Track: Slack Agent for Good**
**Date:** 2026-06-15
**Status:** Approved design — ready for implementation planning

---

## 1. Mission

**MentorOps is a Slack agent for the adults who serve kids — the mentors and coordinators
at a youth mentoring nonprofit, not the children themselves.** These teams run on goodwill
and are stretched thin. When a mentee is struggling — emotionally, academically, or with
basic needs — the mentor's right response depends on knowing the org's protocols,
remembering the mentee's history, and finding the right resource fast. That knowledge is
scattered, and kids fall through the cracks.

MentorOps is the mentor's co-pilot: it helps them respond faster and more completely to
whatever a mentee is facing — while keeping a licensed human in every sensitive loop.
**The mentee never interacts with it. It does not talk to children, diagnose, or provide
therapy.**

**Actors at a glance:**

| Actor | On Slack? | Role |
|---|---|---|
| **Mentor** | Yes | Talks to MentorOps about a mentee; the primary user |
| **Coordinator / safeguarding lead** | Yes | Receives escalations; owns sensitive decisions |
| **Mentee (child)** | **No** | The *subject* of the conversation — never a participant |

**Delivery model (the "last mile"):** value reaches the mentee through the mentor, never
from the agent. `MentorOps → mentor (on Slack) → real-life mentoring → mentee`. The agent
produces hand-offs the mentor delivers; it sends nothing to a child or family directly.

---

## 2. Track & technology compliance

**Track:** Slack Agent for Good (youth wellbeing / nonprofit operations / education).

**Eligible technologies used (all three):**

| Technology | How MentorOps uses it |
|---|---|
| **Slack AI capabilities** | The agent itself: Bolt for Python + `Assistant` class + Claude reasoning, with streaming responses and suggested prompts. |
| **MCP server integration** | A **custom Python MCP server (built by us)** exposing the org's *non-Slack* knowledge — `safeguarding_protocols`, `resource_directory`, `past_proposals` — consumed by the Bolt agent. **Distinct from Slack's MCP server:** Slack's serves Slack *content* and targets external agents; our first-party Bolt app already has native Slack Web API access, so it does **not** consume Slack's MCP server (that would be redundant). Building our own is what earns the "MCP server integration" technology. |
| **Real-Time Search (RTS) API** | **Institutional memory** — real-time search over the org's *own* Slack data, **scoped to the mentee-specific and safeguarding channels the agent belongs to** (past mentee notes, prior similar situations, safeguarding decisions); never the whole workspace. |

> **Platform note:** Slack's RTS API searches the org's own workspace data, **not** the
> public web. External resource/grant discovery is therefore handled separately (curated
> MCP directory for the demo; live web search behind PII redaction as a documented upgrade).

---

## Clarifications

### Session 2026-06-15
- Q: What does MentorOps persist about a child outside Slack (in SQLite)? → A: Only a pseudonymous handle + internal ID; the child's real identifying details stay inside Slack (restricted channel/Canvas) and are never duplicated to local storage.
- Q: Which Slack data should RTS "institutional memory" queries search? → A: Mentee-specific channels + safeguarding channels the agent is a member of — not the whole workspace.
- Q: How does MentorOps determine user roles and enforce access? → A: From Slack-native primitives — user groups (e.g., `@safeguarding-leads`) + restricted-channel membership; no separate roles store.
- Q: Where do the triage severity thresholds (routine/elevated/urgent/crisis) come from? → A: Sourced from the org's safeguarding protocol via the custom MCP server, with a built-in default rubric as fallback.
- Q: How is an imminent-harm crisis detected for the fast-path? → A: Two-stage, fail-safe — a deterministic keyword/pattern pre-filter OR an LLM classifier; either firing activates the fast-path (biased toward false positives).

---

## 3. Users & personas

- **Mentor** (primary) — a volunteer who meets a mentee regularly, logs notes, and raises
  concerns. **Talks to MentorOps DM-first** (private, the natural post-session moment).
- **Program coordinator** — staff who owns escalations, follow-ups, and reporting.
- **Safeguarding lead** — the named human MentorOps routes serious wellbeing concerns to.
- **Executive director / board** (Pillar 5) — consumes impact reports.

**Out of scope as users:** children/mentees themselves, and parents/guardians.

---

## 4. Architecture

```
                         ┌──────────────────────────────────────────┐
                         │              Slack workspace               │
   Mentor / Coordinator  │  DMs · #mentee-* · #safeguarding-leads ·   │
        ───────────────► │  per-mentee Canvases                       │
                         └───────────────┬────────────────────────────┘
                                         │ events (assistant_thread_started,
                                         │ message.im), chat.*Stream
                          ┌──────────────▼───────────────┐
                          │   MentorOps agent (Bolt/Py)   │
                          │   Assistant response loop      │
                          │   • intent router              │
                          │   • safety guardrails          │
                          │   • per-pillar handlers        │
                          └───┬──────────┬─────────┬──────┘
                              │          │         │
              Claude reasoning│   RTS API│   tools │
                              │          │         │
                   ┌──────────▼──┐  ┌────▼─────┐  ┌▼───────────────────────┐
                   │   Claude    │  │  Slack    │  │  Custom MCP server      │
                   │ (opus-4-8)  │  │  RTS      │  │  • safeguarding_protocols│
                   └─────────────┘  │ (own data)│  │  • resource_directory   │
                                    └───────────┘  │  • past_proposals       │
                                                   └───────────┬─────────────┘
                                                               │
                                              ┌────────────────▼───────────┐
                                              │ SQLite: follow-ups, audit   │
                                              │ log, mentee state           │
                                              └─────────────────────────────┘
```

### Core response loop
1. **Receive** input (DM or channel mention) via Bolt event listeners.
2. **Guardrail pre-check** — crisis fast-path scan + channel-scope check.
3. **Route intent** — triage / resource / follow-up / grant / report.
4. **Gather context** — RTS for institutional memory; custom MCP for protocols, resources,
   proposals; SQLite for state.
5. **Reason** with Claude, constrained by per-pillar system prompts and safety rules.
6. **Act** — stream a response, @mention humans, write follow-ups, update the Canvas, and
   append to the audit log.

### 4.1 Presentation layer (UX surfaces)

**MentorOps has no separate web frontend — Slack *is* the UI.** The Python backend renders
every surface through Slack's native APIs, which gives us a polished, accessible,
cross-platform interface for free. Four surfaces:

- **Conversational thread (Block Kit)** — the primary surface. Triage assessments, resource
  results, and grant drafts render as structured Block Kit messages (urgency chips, protocol
  citations, action buttons like *Route to @safeguarding-leads* / *Share & log*), with
  streamed responses via `chat.startStream`.
- **Modals** — short structured input when needed (e.g., confirming an escalation,
  editing a scorecard draft before approval).
- **Canvas** — the durable per-mentee record and the **mentee scorecard** (Pillar 6) live
  here, versioned over time.
- **App Home tab** — a role-aware dashboard: open escalations, follow-ups due, and weekly
  activity. A mentor sees only their own mentees (roles from Slack user groups + channel
  membership, per §6).

A reference mockup of all four surfaces is saved under
`.superpowers/brainstorm/` from the design session. Detailed Block Kit layouts are an
implementation concern, refined during the plan.

**Out of scope:** any web app outside Slack (no admin dashboard, no marketing/landing page).

---

## 5. Pillars

Designed as the full vision; implemented behind a **demo cut line** (Section 7).

### Pillar 1 — Wellbeing triage & safeguarding *(differentiator)*

**Entry point — mentor-initiated, DM-first.** The agent never messages first. The workflow
begins when a mentor opens a **DM with MentorOps** and describes a concern in free text
(e.g., just after a session). The "triage message" is the agent's structured *reply* (step 6
below), not an unprompted alert.

**Flow:** (1) mentor describes a concern → (2) **crisis pre-check** (two-stage fail-safe; if
triggered, skip to the crisis fast-path in §6) → (3) understand mentee/signals/needs →
(4) gather context (RTS + MCP) → (5) assess urgency → (6) reply with the triage Block Kit
message → (7) route to a human → (8) log follow-up + audit + Canvas.

A mentor describes a concern. The agent:
- Assesses **urgency by a rubric** (routine / elevated / urgent / crisis) **sourced from the
  org's safeguarding protocol via the custom MCP server, with a built-in default rubric as
  fallback**. It never diagnoses or counsels.
- Surfaces the org's **own escalation protocol** from the custom MCP server.
- Pulls **institutional memory** via RTS (past notes on this mentee, similar prior cases,
  what the safeguarding leads decided before).
- **Routes** to the right human: posts to `#safeguarding-leads` and @mentions the on-call
  coordinator with a structured summary.
- Logs a **structured follow-up** and an audit entry.

**Invariants:** human in every loop; the agent cannot close a case; severity is a one-way
ratchet (it may raise, never silently lower); crisis input triggers the fast-path.

### Pillar 2 — Resource navigator
A mentor describes a mentee need (college fees, tutoring, food, low-cost counseling). The
agent matches **vetted resources** from the curated MCP `resource_directory`, returns
eligibility + how-to-access, and logs what was shared. (Live web search behind PII
redaction is a documented upgrade.)

**"Share & log" (the last mile):** because the mentee is not on Slack, *sharing* produces a
short, **plain-language hand-off** (what it is, who qualifies, how to apply) that the
**mentor** delivers to the mentee/family in their normal relationship. The agent records
that it was shared and sets a follow-up. The agent never contacts the child or family
directly — no generated outreach in the demo build (family-outreach drafting is a
documented upgrade).

### Pillar 3 — Follow-up & continuity tracking
Tracks open items per mentee, sends **proactive nudges** ("you flagged Maya 5 days ago, no
follow-up logged"), and maintains a living **per-mentee Canvas** as the source of truth.
Uses RTS to reconstruct history when a new mentor inherits a mentee.

### Pillar 4 — Grant & funding support *(original idea)*
Finds grant calls (web, upgrade path), **drafts applications with Slack AI**, references the
org's **past proposals via MCP**, and tracks deadlines. Keeps the program funded.

### Pillar 5 — Mentor–mentee matching & impact reporting
Suggests mentor–mentee matches from interests/availability, and generates **board impact
reports** (Slack AI summarization over logged follow-ups/outcomes + RTS).

### Pillar 6 — Mentee scorecard (holistic progress snapshot)
A strengths-based, **qualitative** one-page view of the whole child, living on the mentee's
Canvas. **Not a grade, not a rank, never a number.**

- **Domains (5):** School & learning · Social-emotional wellbeing · Basic needs / stability
  · Goals & aspirations · Mentoring connection.
- **Per-domain status:** `Thriving / Steady / Needs attention / Unknown` — **strengths
  stated first**, each status backed by the actual source notes. `Unknown` is a first-class
  value so the card never fakes confidence about a mentee we lack data on.
- **Hybrid generation:** the agent synthesizes a **draft** from logged follow-ups + audit
  log + **RTS** institutional memory → presents it in Slack → the **mentor reviews, edits,
  and approves** (nothing saved unapproved) → the approved card is written to the per-mentee
  **Canvas**, timestamped and versioned so progress is visible over time.
- **Safety:** a *support* tool, not a judgment of the child; strengths-first,
  growth-oriented language; confined to restricted channels; **never shared with the
  child**; audit entries on generate + approve; no numeric scores, risk-ratings, or labels.

---

## 6. Safety & privacy model

The feature that separates this from a hackathon toy. Because MentorOps touches minors'
sensitive data:

- **Human-in-the-loop guarantee** — for any wellbeing concern the agent may only assess
  urgency, surface protocol, and route to a named human. It never diagnoses, counsels, or
  closes a case.
- **Crisis fast-path** — detection is **two-stage and fail-safe**: a deterministic
  keyword/pattern pre-filter **OR** an LLM classifier; *either* firing short-circuits all
  routing (deliberately biased toward false positives). It immediately surfaces the crisis
  protocol + on-call human, with a clear "I am not a crisis service" disclaimer.
- **PII minimization** — before any off-platform call (resource/grant web search, upgrade
  path), a redaction pass strips mentee name, DOB, address, school, and other identifiers;
  the agent searches on the *need*, not the *child*. In the curated-directory demo, nothing
  leaves Slack at all.
- **No off-platform identity storage** — SQLite persists only a **pseudonymous handle +
  internal ID** per mentee. A child's real identifying details live solely inside Slack
  (the restricted channel/Canvas the org already controls) and are never duplicated to
  local storage.
- **Channel-scoped access** — safeguarding content and mentee records are confined to
  restricted channels; the agent refuses to surface sensitive records in open channels.
  Roles are derived from **Slack-native primitives** — user groups (e.g.,
  `@safeguarding-leads`) plus restricted-channel membership — not a separate roles store.
- **Immutable audit trail** — every escalation, resource shared, and follow-up is logged
  (who / what / when) for accountability and to demonstrate continuity.
- **Severity ratchet** — the agent may raise a concern's severity but never silently lower
  it; downgrades require a human.

---

## 7. Demo cut line (de-risking the full vision)

We design all six pillars but implement in strict priority order:

| Priority | Pillars | Rationale |
|---|---|---|
| **Above the line — MUST work for demo** | **1 + 2** | The heart of the product; showcases all three technologies (Slack AI + MCP + RTS) + the safety model. |
| **Then** | **3** | Cheap to add, huge operational credibility ("nothing falls through the cracks"). |
| **Upside** | **4 + 5 + 6** | Funding sustainability, board reporting, and the mentee scorecard. Pillar 6 depends on Pillar 3's logged data but is the **most demo-friendly upside item** — a strong closing beat. |

If only pillars 1–2 ship, MentorOps is still a complete, demo-able, award-worthy agent.

---

## 8. Tech stack

- **UI / presentation:** **Slack-native only** — Block Kit messages, modals, Canvas, and
  the App Home tab. No separate web frontend (see §4.1).
- **Agent runtime:** Bolt for **Python**, `Assistant` class; Socket Mode for local dev,
  hosted endpoint for the demo.
- **Reasoning:** **Claude `claude-opus-4-8`** for triage/drafting; a smaller model
  (`claude-haiku-4-5`) for cheap intent classification.
- **Custom MCP server:** Python MCP server exposing `safeguarding_protocols`,
  `resource_directory`, `past_proposals`; backed by files/SQLite with embedding-based
  retrieval.
- **RTS:** Slack Real-Time Search API for institutional-memory queries.
- **Storage:** SQLite for mentee follow-ups, audit log, and state; per-mentee state mirrored
  to a Slack Canvas.
- **Secrets:** environment variables; no minor PII persisted off-platform.

---

## 9. Data model (initial)

- **mentee** — internal id, **pseudonymous handle** (no real PII stored here), assigned
  mentor, channel, canvas_id, status.
- **followup** — id, mentee_id, raised_by, summary, severity, due_at, status, created_at.
- **audit_event** — id, actor, action, target, severity_before/after, payload, ts.
- **resource** (MCP) — id, category, title, eligibility, how_to_access, vetted_by.
- **protocol** (MCP) — id, trigger, steps, escalation_target, references.
- **scorecard** — id, mentee_id, generated_at, generated_by, approved_by, canvas_version.
- **scorecard_domain** — scorecard_id, domain, status_enum, strengths, concerns, source_refs.

---

## 10. Demo plan

Seed a fictional nonprofit, **"BrightPath Mentors"**, with:
- Channels: `#general`, `#mentee-maya`, `#mentee-jordan`, `#safeguarding-leads`.
- Seeded safeguarding protocols + a vetted resource directory in the MCP server.
- A handful of mentees with prior Slack history so **RTS has real institutional memory to
  find**.

**Demo narrative (golden path):** A mentor messages MentorOps about Maya (15) —
college-app stress, can't afford fees, "seemed really down today." The agent:
1. Detects a wellbeing signal → triages as *elevated*, surfaces BrightPath's check-in
   protocol (MCP), pulls Maya's past notes (RTS), routes to `#safeguarding-leads`,
   logs a follow-up.
2. Surfaces vetted resources (MCP): fee-waiver program + free local college-prep.
3. Updates Maya's Canvas and the audit log.
Then a second turn shows the proactive follow-up nudge (Pillar 3).

**Closing beat (if Pillar 6 ships):** the mentor asks for Maya's scorecard. The agent
synthesizes a strengths-first draft across the five domains from the logged history + RTS,
the mentor tweaks one line and approves, and it's written to Maya's Canvas — visually
summarizing the whole story without a single number.

---

## 11. Out of scope / roadmap

- Kid-facing or parent-facing interfaces.
- Any diagnosis, therapy, or autonomous case closure.
- Live web search for resources/grants (upgrade path behind PII redaction).
- Marketplace submission / multi-tenant deployment.
- Pillars 4–5 if time-constrained.

---

## 12. Success criteria

- **Judging alignment:** uses all three eligible technologies meaningfully; clear social
  impact; a defensible safety story most entries will lack.
- **Demo:** the golden path runs reliably end-to-end with seeded data.
- **Trust:** every sensitive action has a human in the loop and an audit entry.
- **Scope safety:** pillars 1–2 fully working constitutes a complete submission.

---

## 13. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Over-scoping (5 pillars) | Hard demo cut line; 1–2 is a complete product. |
| RTS misunderstood as web search | Corrected: RTS = own-workspace memory; web search separated. |
| Sensitive-topic liability | Human-in-loop guarantee, no diagnosis/therapy, crisis fast-path, disclaimers. |
| Live-demo flakiness | Curated MCP directory (no external calls) for the demo. |
| RTS has nothing to find | Seed BrightPath Slack history before the demo. |

---

## 14. Hackathon execution & judging strategy

Source: office-hours review against the real rules at https://slackhack.devpost.com/.

### Hard facts
- **Deadline:** 2026-07-13, 5:00pm PDT (~3 weeks from design).
- **Deliverables:** track selection; text description; **~3-min demo video**; **architecture
  diagram** (have one, §4 + wireframe); **URL to a Slack dev sandbox** with access for
  `slackhack@salesforce.com` and `testing@devpost.com`. Track: **Slack Agent for Good**.
- **Judges run the sandbox themselves.** It must survive poking, not just demo on rails.

### Judging criteria (four, equal/unweighted) + how MentorOps wins each
| Criterion | Bonus prize | MentorOps play |
|---|---|---|
| Technological Implementation | Best Tech Impl ($2k) | Real (small) MCP server + real RTS wiring + clean code. Stub minimally; judges run it. |
| Design / UX | **Best UX ($2k)** | Polished Block Kit (triage card, resource cards), Canvas scorecard, App Home. UX is 1/4 of score — not optional. |
| Potential Impact | — | Youth wellbeing + the safety/ethics posture (never talks to kids, human-in-loop). |
| Quality of the Idea | Most Innovative ($2k) | The reframe most entries miss: serve the adults who serve kids; RTS as institutional memory. |

### Build scope (decision: **hero + planned stretch**)
- **Hero (must be fully real):** Pillar 1 wellbeing triage end-to-end — genuine MCP
  protocol lookup + genuine RTS institutional-memory + a **working** crisis/escalation
  guardrail + polished Block Kit, routing to `#safeguarding-leads`.
- **Planned stretch (buys Design + Impact points):** Pillar 2 resource navigator, then the
  Pillar 6 scorecard Canvas as the visual closer.
- **Cut to spoken story / spec only (do NOT build this cycle):** Pillars 4 & 5; the
  immutable audit log, channel-scoped role system, and two-stage crisis classifier stay
  **real-but-minimal** (a credible working guardrail), described in full in the video, not
  gold-plated in code.

> Note: this supersedes §7's "1+2 above the line" framing for the *hackathon build*. §7
> remains the product cut line; §14 is the contest-calibrated subset.

### Because judges run it, not just watch it
- Seed `BrightPath Mentors` sandbox data early (channels, protocols, resource directory,
  and **prior Slack history so RTS returns real hits**). This is build work, not an
  afterthought.
- The guardrail must actually fire if a judge types something alarming. A safety story that
  breaks under testing costs Impact + Tech points.

### ~3-minute video script (the golden path is the script)
1. (0:00) The problem in one line: stretched mentors, kids fall through cracks.
2. (0:20) Mentor DMs MentorOps the messy Maya concern → triage card (urgency + protocol via
   MCP + past note via RTS) → route to `#safeguarding-leads`.
3. (1:20) Resource navigator: vetted matches + plain-language hand-off + logged.
4. (2:00) Scorecard Canvas closer (strengths-based, no numbers).
5. (2:40) The ethics line: never talks to kids, human in every loop. Close.

### 3-week milestones (calibrated to 2026-07-13)
- **Week 1:** Bolt skeleton + Slack sandbox + MCP server (protocols/resources) + Pillar 1
  triage working on seeded data.
- **Week 2:** RTS institutional memory + guardrail + Block Kit polish + Pillar 2 resources.
- **Week 3:** Scorecard Canvas + App Home + seed-data hardening + record video + write-up +
  grant judges sandbox access.
