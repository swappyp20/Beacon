def home_view(open_followups: list) -> dict:
    blocks = [{"type": "header", "text": {"type": "plain_text", "text": "Beacon — Home"}}]
    if open_followups:
        blocks.append({"type": "section", "text": {"type": "mrkdwn",
            "text": f":alarm_clock: *{len(open_followups)} follow-up(s) open*"}})
        for f in open_followups[:10]:
            blocks.append({"type": "context", "elements": [{"type": "mrkdwn",
                "text": f"• mentee #{f['mentee_id']} — {f['summary']} ({f['severity']})"}]})
    else:
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": "No open follow-ups. Nothing dropped."}})
    blocks.append({"type": "context", "elements": [{"type": "mrkdwn",
        "text": "Beacon never talks to kids. A human owns every escalation."}]})
    return {"type": "home", "blocks": blocks}
