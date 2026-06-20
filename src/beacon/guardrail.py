import re

# Deterministic pre-filter. Deliberately broad: false positives are acceptable,
# misses are not (spec §6 crisis fast-path).
_CRISIS_PATTERNS = [
    r"\bkill (her|him|them|my)self\b",
    r"\bsuicid", r"\bend (her|his|their|my) life\b",
    r"\bhurt (her|him|them|my)self\b", r"\bself[-\s]?harm",
    r"\bcut(s|ting)?\b.*\b(arm|wrist|herself|himself)\b",
    r"\btook .*(pills|overdose)\b", r"\boverdose",
    r"\bno point in living\b", r"\bbetter off without (me|him|her)\b",
    r"\b(hits|beats|touches) (her|him|them)\b", r"\babuse",
    r"\bscared to go home\b", r"\bnowhere to go\b", r"\brun away\b",
]
_RX = [re.compile(p, re.IGNORECASE) for p in _CRISIS_PATTERNS]


def keyword_crisis(text: str) -> bool:
    return any(rx.search(text or "") for rx in _RX)


def is_crisis(text: str, llm) -> bool:
    """Two-stage, fail-safe: EITHER the keyword pre-filter OR the LLM classifier
    firing activates the crisis fast-path. Biased toward false positives."""
    if keyword_crisis(text):
        return True
    try:
        return bool(llm.classify_crisis(text))
    except Exception:
        # An errored classifier yields no extra signal; we never silently suppress
        # a crisis (the keyword result above is already authoritative when True).
        return False
