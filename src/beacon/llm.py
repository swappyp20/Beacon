import json
import re
from anthropic import Anthropic
from .config import config


def _loads_lenient(text: str) -> dict:
    """Parse JSON the model returned, tolerating ```json fences or stray prose.
    Falls back to an empty extraction (no handle) so triage never crashes."""
    text = (text or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.split("\n", 1)[-1] if "\n" in text else text
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
    return {"handle": None, "signals": [], "needs": []}


class LLM:
    def __init__(self, client: "Anthropic | None" = None):
        self.client = client or Anthropic(api_key=config.anthropic_key)

    def classify_crisis(self, text: str) -> bool:
        """Cheap haiku call: is this an imminent-harm crisis? Bias toward YES."""
        msg = self.client.messages.create(
            model=config.model_classify, max_tokens=5,
            system=("You flag imminent-harm crises for a child-safeguarding tool. "
                    "Reply ONLY 'YES' or 'NO'. When unsure, reply YES."),
            messages=[{"role": "user", "content": text}],
        )
        return msg.content[0].text.strip().upper().startswith("Y")

    def extract(self, mentor_text: str) -> dict:
        """Opus call: pull mentee handle, signals, needs from free text.
        Returns {handle, signals:[...], needs:[...]}. Never invents a handle."""
        sys = ("Extract structured fields from a youth mentor's note. "
               "Return JSON {\"handle\": <lowercase first name or null>, "
               "\"signals\": [..wellbeing observations..], "
               "\"needs\": [..concrete needs like 'college fees'..]}. "
               "Do not guess a handle that isn't named.")
        msg = self.client.messages.create(
            model=config.model_reason, max_tokens=400,
            system=sys, messages=[{"role": "user", "content": mentor_text}],
        )
        return _loads_lenient(msg.content[0].text)

    def assess_severity(self, mentor_text: str, rubric: dict) -> str:
        """Opus call: choose one severity word from the rubric. Never diagnoses."""
        sys = ("Assess urgency for a youth-safeguarding triage. Choose exactly one of: "
               "routine, elevated, urgent, crisis. You do NOT diagnose. Reply with one word.\n"
               "Rubric:\n" + json.dumps(rubric))
        msg = self.client.messages.create(
            model=config.model_reason, max_tokens=5,
            system=sys, messages=[{"role": "user", "content": mentor_text}],
        )
        word = msg.content[0].text.strip().lower()
        return word if word in rubric else "elevated"

    def categorize_need(self, need: str) -> str:
        """Map a free-text need to a resource category keyword."""
        msg = self.client.messages.create(
            model=config.model_classify, max_tokens=10,
            system=("Map a youth need to ONE category keyword from: "
                    "college-cost, college-prep, crisis, food, housing, tutoring, jobs, health. "
                    "Reply with the single keyword."),
            messages=[{"role": "user", "content": need}],
        )
        return msg.content[0].text.strip().lower()

    def synthesize_scorecard(self, handle: str, memory: list, followups: list) -> dict:
        sys = ("Draft a STRENGTHS-FIRST youth scorecard across exactly these 5 domains: "
               "School & learning; Social-emotional wellbeing; Basic needs / stability; "
               "Goals & aspirations; Mentoring connection. For each, return "
               "{status, strengths, concerns} where status is one of "
               "Thriving|Steady|Needs attention|Unknown. Use Unknown when there is no "
               "evidence. NO numbers, NO grades, NO ranking. Return a JSON object keyed by domain.")
        payload = {"handle": handle, "memory": memory, "followups": followups}
        msg = self.client.messages.create(
            model=config.model_reason, max_tokens=700,
            system=sys, messages=[{"role": "user", "content": json.dumps(payload)}],
        )
        return json.loads(msg.content[0].text)
