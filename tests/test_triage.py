from beacon.triage import run_triage, TriageResult


class FakeLLM:
    def __init__(self, sev="elevated", crisis=False):
        self.sev = sev
        self.crisis = crisis

    def classify_crisis(self, text):
        return self.crisis

    def extract(self, text):
        return {"handle": "maya", "signals": ["seemed down"], "needs": ["college fees"]}

    def assess_severity(self, text, rubric):
        return self.sev


class FakeKnowledge:
    def get_protocol(self, severity):
        return {"id": f"p-{severity}", "steps": ["Notify the lead"],
                "escalation_target": "#safeguarding-leads", "rubric": {}}

    def find_resources(self, category):
        return []


class FakeRTS:
    def __init__(self, hits):
        self.hits = hits

    def recall(self, q, limit=5):
        return self.hits


def test_non_crisis_triage_produces_severity_protocol_and_rts_memory():
    r = run_triage("Met Maya, college fees, seemed down", mentor="U1",
                   llm=FakeLLM(sev="elevated"), knowledge=FakeKnowledge(),
                   rts=FakeRTS([{"text": "Maya quiet last week", "channel": "C_MAYA"}]))
    assert isinstance(r, TriageResult)
    assert r.crisis is False
    assert r.severity == "elevated"
    assert r.handle == "maya"
    assert r.protocol["escalation_target"] == "#safeguarding-leads"
    assert r.memory and r.memory[0]["text"].startswith("Maya quiet")
    assert r.needs == ["college fees"]


def test_crisis_short_circuits_to_crisis_protocol():
    r = run_triage("She said she wants to kill herself", mentor="U1",
                   llm=FakeLLM(crisis=True), knowledge=FakeKnowledge(), rts=FakeRTS([]))
    assert r.crisis is True
    assert r.severity == "crisis"
    assert r.protocol["id"] == "p-crisis"


def test_unknown_mentee_is_flagged_not_invented():
    class NoHandleLLM(FakeLLM):
        def extract(self, text):
            return {"handle": None, "signals": [], "needs": []}

    r = run_triage("a vague note", mentor="U1", llm=NoHandleLLM(),
                   knowledge=FakeKnowledge(), rts=FakeRTS([]))
    assert r.handle is None
    assert r.needs_clarification is True
