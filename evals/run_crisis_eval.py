"""Run the crisis eval. Every case MUST trigger the guardrail (keyword OR LLM).
Exit non-zero if any case slips through. Run before recording the demo.

Requires ANTHROPIC_API_KEY in .env. Usage: python evals/run_crisis_eval.py
"""
import json
import sys
from pathlib import Path
from beacon.guardrail import is_crisis
from beacon.llm import LLM


def main():
    cases = json.loads((Path(__file__).parent / "crisis_cases.json").read_text())
    llm = LLM()
    results = [(t, is_crisis(t, llm=llm)) for t in cases]
    for text, fired in results:
        print("FIRE " if fired else "MISS ", text)
    misses = [t for t, fired in results if not fired]
    if misses:
        print(f"\nFAILED: {len(misses)} case(s) did not fire:")
        for m in misses:
            print("  -", m)
        sys.exit(1)
    print(f"\nPASS: all {len(cases)} crisis cases fired.")


if __name__ == "__main__":
    main()
