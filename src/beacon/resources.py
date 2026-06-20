def navigate_resources(mentor_text: str, llm, knowledge) -> list[dict]:
    """Pillar 2: turn a stated need into vetted resources. Searches the NEED,
    not the child (spec §6 privacy). Returns [] when nothing matches."""
    fields = llm.extract(mentor_text)
    out, seen = [], set()
    for need in fields.get("needs", []) or [mentor_text]:
        category = llm.categorize_need(need)
        for r in knowledge.find_resources(category):
            if r["id"] not in seen:
                seen.add(r["id"])
                out.append(r)
    return out


def handoff_text(resource: dict) -> str:
    """Plain-language hand-off the MENTOR gives the mentee/family (spec decision #15).
    The agent never contacts a child or family directly."""
    return (f"*{resource['title']}*\n"
            f"Who qualifies: {resource.get('eligibility', '—')}\n"
            f"How to access: {resource.get('how_to_access', '—')}")
