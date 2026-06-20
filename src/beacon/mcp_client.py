import asyncio
import json
from typing import Any


class KnowledgeClient:
    """Synchronous wrapper around an MCP session exposing our two knowledge tools.

    `session` must provide `async call_tool(name, args)`. All calls run on a single
    dedicated event loop owned by this client, so a persistent stdio session stays
    bound to exactly one loop for its lifetime.
    """

    def __init__(self, session: Any, loop: "asyncio.AbstractEventLoop | None" = None):
        self.session = session
        self._loop = loop or asyncio.new_event_loop()

    def _call(self, name: str, args: dict) -> Any:
        result = self._loop.run_until_complete(self.session.call_tool(name, args))
        # Fake session (tests) hands back a plain dict; the real mcp SDK hands back
        # a CallToolResult object.
        if isinstance(result, dict):
            sc = result.get("structuredContent", result)
        else:
            sc = getattr(result, "structuredContent", None)
            if sc is None:
                content = getattr(result, "content", None) or []
                text = "".join(getattr(c, "text", "") for c in content)
                sc = json.loads(text) if text else None
        # FastMCP wraps non-object (and some object) returns under {"result": ...}.
        if isinstance(sc, dict) and set(sc.keys()) == {"result"}:
            sc = sc["result"]
        return sc

    def get_protocol(self, severity: str) -> dict:
        return self._call("get_protocol", {"severity": severity}) or {}

    def find_resources(self, category: str) -> list[dict]:
        return self._call("find_resources", {"category": category}) or []

    @classmethod
    def connect_stdio(cls, command: str) -> "KnowledgeClient":
        """Launch the MCP server as a subprocess over stdio and return a client.

        The transport stays open for the client's lifetime, bound to one loop.
        See the mcp Python SDK stdio_client. Confirm the CallToolResult shape
        against the installed SDK during live integration.
        """
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        loop = asyncio.new_event_loop()
        parts = command.split()
        params = StdioServerParameters(command=parts[0], args=parts[1:])
        cm = stdio_client(params)
        read, write = loop.run_until_complete(cm.__aenter__())
        session = ClientSession(read, write)
        loop.run_until_complete(session.__aenter__())
        loop.run_until_complete(session.initialize())
        client = cls(session=session, loop=loop)
        client._cm = cm  # keep the transport context-manager alive
        return client
