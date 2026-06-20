import json
from anthropic import Anthropic
from .config import config


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
        return json.loads(msg.content[0].text)

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
