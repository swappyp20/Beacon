from dataclasses import dataclass, field
from .guardrail import is_crisis
from .rubric import resolve_rubric


@dataclass
class TriageResult:
    handle: "str | None"
    severity: str
    crisis: bool
    protocol: dict
    memory: list
    signals: list = field(default_factory=list)
    needs: list = field(default_factory=list)
    needs_clarification: bool = False


def run_triage(mentor_text: str, mentor: str, llm, knowledge, rts) -> TriageResult:
    """Pillar 1 orchestration (spec §5 Pillar 1):
    crisis pre-check -> understand -> gather context (RTS+MCP) -> assess -> result."""
    # 1. Crisis fast-path (fail-safe). Short-circuits normal flow.
    if is_crisis(mentor_text, llm=llm):
        protocol = knowledge.get_protocol("crisis")
        return TriageResult(handle=_safe_handle(llm, mentor_text), severity="crisis",
                            crisis=True, protocol=protocol, memory=[])

    # 2. Understand
    fields = llm.extract(mentor_text)
    handle = fields.get("handle")

    # 3 + 4. Gather context (RTS scoped memory) and assess severity (MCP rubric).
    if handle:
        query = f"{handle} {' '.join(fields.get('signals', []))}".strip()
        memory = rts.recall(query, limit=5)
    else:
        memory = []
    base_protocol = knowledge.get_protocol("elevated")
    rubric = resolve_rubric(base_protocol.get("rubric"))
    severity = llm.assess_severity(mentor_text, rubric)
    protocol = knowledge.get_protocol(severity)

    return TriageResult(
        handle=handle, severity=severity, crisis=False, protocol=protocol,
        memory=memory, signals=fields.get("signals", []), needs=fields.get("needs", []),
        needs_clarification=(handle is None),
    )


def _safe_handle(llm, text):
    try:
        return llm.extract(text).get("handle")
    except Exception:
        return None
