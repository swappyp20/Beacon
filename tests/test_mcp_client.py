from beacon.mcp_client import KnowledgeClient


class FakeSession:
    async def call_tool(self, name, args):
        from mcp_server.server import load_protocols, find_protocol, load_resources, match_resources

        if name == "get_protocol":
            return {"structuredContent": find_protocol(load_protocols(), args["severity"]) or {}}
        if name == "find_resources":
            return {"structuredContent": match_resources(load_resources(), args["category"])}
        raise AssertionError(name)


def test_get_protocol_returns_steps():
    client = KnowledgeClient(session=FakeSession())
    p = client.get_protocol("crisis")
    assert p["escalation_target"] == "#safeguarding-leads"


def test_find_resources_returns_matches():
    client = KnowledgeClient(session=FakeSession())
    hits = client.find_resources("college-cost")
    assert hits and hits[0]["id"] == "nacac-fee-waiver"
