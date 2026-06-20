DOMAINS = ["School & learning", "Social-emotional wellbeing", "Basic needs / stability",
           "Goals & aspirations", "Mentoring connection"]
STATUSES = ["Thriving", "Steady", "Needs attention", "Unknown"]


def synthesize_card(handle: str, memory: list, followups: list, llm) -> dict:
    """Pillar 6: agent drafts; a mentor approves before it is saved (spec decision #11).
    Strengths-first, qualitative, never numeric. Unknown when there is no evidence."""
    raw = llm.synthesize_scorecard(handle, memory, followups)
    card = {}
    for d in DOMAINS:
        entry = raw.get(d, {}) or {}
        status = entry.get("status") if entry.get("status") in STATUSES else "Unknown"
        card[d] = {"status": status, "strengths": entry.get("strengths", ""), "concerns": entry.get("concerns", "")}
    return card


def render_canvas_markdown(handle: str, card: dict) -> str:
    title = handle.capitalize()
    lines = [f"# {title} — Progress Snapshot (draft v1)", "",
             "_Strengths-first. No scores or grades. `Unknown` means we don't have evidence yet._", ""]
    for d in DOMAINS:
        e = card[d]
        lines.append(f"## {d}: {e['status']}")
        lines.append(f"- Strengths: {e['strengths'] or '—'}")
        if e["concerns"]:
            lines.append(f"- Watch: {e['concerns']}")
        lines.append("")
    return "\n".join(lines)
