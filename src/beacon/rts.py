import httpx

# NOTE: Slack's Real-Time Search API searches the org's OWN workspace data.
# Confirm the exact endpoint/params against current docs at
# https://docs.slack.dev/ai/slack-mcp-server/ during integration. The client is
# written against the documented behavior: a scoped search returning messages.
# If RTS access isn't provisioned in the sandbox, set use_fallback=True and the
# client uses the Web API search.messages with an `in:` channel filter instead.
RTS_ENDPOINT = "https://slack.com/api/search.realtime"  # confirm in docs
SEARCH_FALLBACK_ENDPOINT = "https://slack.com/api/search.messages"


class RTSClient:
    def __init__(self, token: str, http=None, scope_channels: tuple = (), use_fallback: bool = False):
        self.token = token
        self.http = http or httpx.Client(timeout=10)
        self.scope_channels = scope_channels
        self.use_fallback = use_fallback

    def recall(self, query: str, limit: int = 5) -> list[dict]:
        """Return up to `limit` prior messages from the scoped channels that match
        `query`. Empty list when nothing is found (caller must NOT fabricate)."""
        headers = {"Authorization": f"Bearer {self.token}"}
        if self.use_fallback:
            scoped_q = query + "".join(f" in:{c}" for c in self.scope_channels)
            r = self.http.post(SEARCH_FALLBACK_ENDPOINT, json={"query": scoped_q, "count": limit}, headers=headers)
            data = r.json()
            matches = data.get("messages", {}).get("matches", [])
            return [{"text": m.get("text", ""), "channel": m.get("channel", {}).get("id", "")} for m in matches][:limit]
        body = {"query": query, "channels": list(self.scope_channels), "limit": limit}
        r = self.http.post(RTS_ENDPOINT, json=body, headers=headers)
        r.raise_for_status()
        data = r.json()
        msgs = data.get("messages", [])
        return [{"text": m.get("text", ""), "channel": m.get("channel", "")} for m in msgs][:limit]
