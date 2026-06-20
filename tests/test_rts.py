from beacon.rts import RTSClient


class FakeHTTP:
    def __init__(self, payload):
        self.payload = payload
        self.last = None

    def post(self, url, json, headers):
        self.last = {"url": url, "json": json, "headers": headers}

        class R:
            def __init__(s, p):
                s._p = p

            def json(s):
                return s._p

            def raise_for_status(s):
                return None

        return R(self.payload)


def test_search_scopes_to_allowed_channels_only():
    http = FakeHTTP({"messages": [{"text": "Maya seemed quiet last week", "channel": "C_MAYA"}]})
    rts = RTSClient(token="xoxb", http=http, scope_channels=("C_MAYA",))
    hits = rts.recall("Maya mood", limit=5)
    assert hits[0]["text"].startswith("Maya seemed quiet")
    assert "C_MAYA" in str(http.last["json"])


def test_recall_returns_empty_list_when_no_hits():
    http = FakeHTTP({"messages": []})
    rts = RTSClient(token="xoxb", http=http, scope_channels=("C_MAYA",))
    assert rts.recall("nothing here", limit=5) == []
