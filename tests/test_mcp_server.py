from mcp_server.server import load_protocols, load_resources, find_protocol, match_resources


def test_protocols_load_and_lookup_by_severity():
    protocols = load_protocols()
    p = find_protocol(protocols, severity="crisis")
    assert p["escalation_target"] == "#safeguarding-leads"
    assert "Do NOT counsel" in " ".join(p["steps"])


def test_resources_match_by_category():
    res = load_resources()
    hits = match_resources(res, category="college-cost")
    assert any(r["id"] == "nacac-fee-waiver" for r in hits)
