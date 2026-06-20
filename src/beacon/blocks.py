_CHIP = {"routine": "Routine", "elevated": "Elevated", "urgent": "Urgent", "crisis": "Crisis"}


def _section(text: str) -> dict:
    return {"type": "section", "text": {"type": "mrkdwn", "text": text}}


def _context(text: str) -> dict:
    return {"type": "context", "elements": [{"type": "mrkdwn", "text": text}]}


def triage_card(r) -> list[dict]:
    handle = r.handle or "this mentee"
    if r.crisis:
        return [
            _section(f":rotating_light: *Crisis signal* on *{handle}* — taking the crisis fast-path."),
            _section("*This is not a diagnosis. I am not a crisis service.*"),
            _section("*Protocol:* " + " · ".join(r.protocol.get("steps", []))),
            _context(f"Routing now to {r.protocol.get('escalation_target', '#safeguarding-leads')}"),
            {"type": "actions", "elements": [
                {"type": "button", "style": "danger",
                 "text": {"type": "plain_text", "text": "Notify @safeguarding-leads now"},
                 "action_id": "route_crisis", "value": handle}]},
        ]
    refs = ", ".join(r.protocol.get("references", [])) or "org protocol"
    mem_lines = "\n".join(f"> {m['text']}" for m in r.memory) if r.memory else "_no prior history found_"
    return [
        _section(f"Reviewed what you shared about *{handle}*."),
        _section(f"*Urgency: {_CHIP.get(r.severity, r.severity)}*  ·  _this is not a diagnosis_"),
        _section("*Protocol step:* " + " · ".join(r.protocol.get("steps", []))),
        _context(f":clipboard: Protocol `{r.protocol.get('id', '?')}` via *MCP* ({refs})"),
        _section("*Institutional memory:*\n" + mem_lines),
        _context(f":clock3: via *RTS* over scoped channels ({len(r.memory)} hit(s))"),
        {"type": "actions", "elements": [
            {"type": "button", "style": "primary",
             "text": {"type": "plain_text", "text": "Route to @safeguarding-leads"},
             "action_id": "route_concern", "value": handle},
            {"type": "button",
             "text": {"type": "plain_text", "text": "View protocol"},
             "action_id": "view_protocol", "value": r.protocol.get("id", "")}]},
    ]


def resource_cards(resources: list[dict]) -> list[dict]:
    if not resources:
        return [_section("No vetted resources matched yet. I only surface vetted options.")]
    blocks = [_section("*Vetted resources matched to the need:*")]
    for r in resources:
        blocks.append(_section(f"*{r['title']}*\n_Eligible:_ {r.get('eligibility', '—')} · :white_check_mark: vetted by {r.get('vetted_by', 'staff')}"))
        blocks.append({"type": "actions", "elements": [
            {"type": "button", "text": {"type": "plain_text", "text": "Get hand-off sheet"},
             "action_id": "resource_handoff", "value": r["id"]}]})
    return blocks
