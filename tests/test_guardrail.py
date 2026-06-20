import json
from pathlib import Path
from beacon.guardrail import keyword_crisis, is_crisis

CASES = json.loads(Path("evals/crisis_cases.json").read_text())


class FakeLLM:
    def __init__(self, verdict):
        self.verdict = verdict

    def classify_crisis(self, text):
        return self.verdict


def test_keyword_layer_catches_obvious_phrasings():
    assert keyword_crisis("she wants to kill herself")
    assert keyword_crisis("he is going to hurt himself")
    assert not keyword_crisis("she is stressed about college fees")


def test_is_crisis_fires_when_either_layer_fires():
    text = "there's no point in living anymore"
    assert is_crisis(text, llm=FakeLLM(verdict=True))


def test_benign_text_is_not_crisis_when_both_layers_clear():
    assert not is_crisis("she's worried about her math grade", llm=FakeLLM(verdict=False))


def test_every_eval_case_fires_via_keyword_or_llm():
    # With the LLM stubbed True, all must fire; this documents the fail-safe contract.
    for text in CASES:
        assert is_crisis(text, llm=FakeLLM(verdict=True)), text
