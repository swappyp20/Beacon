from beacon.resources import navigate_resources, handoff_text


class FakeKnowledge:
    def find_resources(self, category):
        if category == "college-cost":
            return [{"id": "nacac-fee-waiver", "title": "NACAC Fee Waiver",
                     "eligibility": "income-qualified", "how_to_access": "counselor submits form",
                     "vetted_by": "staff"}]
        return []


class FakeLLM:
    def extract(self, text):
        return {"handle": "maya", "signals": [], "needs": ["college fees"]}

    def categorize_need(self, need):
        return "college-cost"


def test_navigate_returns_vetted_matches_for_the_need():
    res = navigate_resources("Maya can't afford college app fees", llm=FakeLLM(), knowledge=FakeKnowledge())
    assert res and res[0]["id"] == "nacac-fee-waiver"


def test_handoff_text_is_plain_language_and_actionable():
    txt = handoff_text({"title": "NACAC Fee Waiver", "eligibility": "income-qualified",
                        "how_to_access": "counselor submits form"})
    assert "NACAC Fee Waiver" in txt
    assert "income-qualified" in txt
    assert "counselor submits form" in txt
