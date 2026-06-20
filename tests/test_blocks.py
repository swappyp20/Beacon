from beacon.blocks import triage_card
from beacon.triage import TriageResult


def test_triage_card_shows_urgency_protocol_and_rts_sources():
    r = TriageResult(handle="maya", severity="elevated", crisis=False,
                     protocol={"id": "checkin-elevated", "escalation_target": "#safeguarding-leads",
                               "steps": ["Notify the lead"], "references": ["Handbook s.3"]},
                     memory=[{"text": "Maya quiet last week", "channel": "C_MAYA"}],
                     signals=["seemed down"], needs=["college fees"])
    blocks = triage_card(r)
    flat = str(blocks)
    assert "Elevated" in flat                       # urgency chip
    assert "checkin-elevated" in flat               # MCP source visible
    assert "RTS" in flat                            # RTS provenance visible
    assert "Maya quiet last week" in flat           # the actual memory hit
    assert "Route to" in flat                       # escalation action button
    assert "not a diagnosis" in flat.lower()        # safety disclaimer


def test_crisis_card_leads_with_crisis_disclaimer():
    r = TriageResult(handle="maya", severity="crisis", crisis=True,
                     protocol={"id": "crisis", "escalation_target": "#safeguarding-leads",
                               "steps": ["@mention the lead now"], "references": []}, memory=[])
    flat = str(triage_card(r))
    assert "not a crisis service" in flat.lower()
    assert "safeguarding" in flat.lower()
