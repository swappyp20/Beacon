SEVERITIES = ["routine", "elevated", "urgent", "crisis"]


def default_rubric() -> dict:
    return {
        "routine": "General check-in. No wellbeing flag. Log and continue.",
        "elevated": "A non-crisis wellbeing signal (low mood, withdrawal, stress, basic-needs gap). Surface protocol + notify a lead.",
        "urgent": "Serious but not imminent (escalating distress, safety worry without immediate danger). Escalate to a named lead promptly.",
        "crisis": "Imminent harm: self-harm, suicide, abuse disclosure, immediate danger. Crisis fast-path + on-call human now.",
    }


def resolve_rubric(mcp_rubric: "dict | None") -> dict:
    """Org rubric from MCP wins per-level; the built-in default fills any gap so
    triage always works out of the box (spec decision #14)."""
    merged = default_rubric()
    if mcp_rubric:
        for level, text in mcp_rubric.items():
            if level in merged and text:
                merged[level] = text
    return merged


def rank(severity: str) -> int:
    return SEVERITIES.index(severity) if severity in SEVERITIES else 1
