from beacon.scorecard import DOMAINS, STATUSES, synthesize_card, render_canvas_markdown


class FakeLLM:
    def synthesize_scorecard(self, handle, memory, followups):
        return {
            "School & learning": {"status": "Steady", "strengths": "motivated re college", "concerns": "app fees"},
            "Social-emotional wellbeing": {"status": "Needs attention", "strengths": "opens up with mentor", "concerns": "low mood flagged"},
            "Basic needs / stability": {"status": "Unknown", "strengths": "", "concerns": ""},
            "Goals & aspirations": {"status": "Thriving", "strengths": "wants nursing", "concerns": ""},
            "Mentoring connection": {"status": "Steady", "strengths": "regular sessions", "concerns": ""},
        }


def test_card_covers_all_five_domains_with_valid_statuses():
    card = synthesize_card("maya", memory=[], followups=[], llm=FakeLLM())
    assert set(card.keys()) == set(DOMAINS)
    for d in DOMAINS:
        assert card[d]["status"] in STATUSES


def test_canvas_markdown_is_strengths_first_and_has_no_numbers():
    card = synthesize_card("maya", memory=[], followups=[], llm=FakeLLM())
    md = render_canvas_markdown("maya", card)
    assert "Maya" in md
    assert "Strengths" in md
    assert not any(ch.isdigit() for ch in md.replace("v1", "")), "scorecard must contain no scores/numbers"
