import json
from pathlib import Path

DATA = Path(__file__).parent / "data"


def load_protocols() -> list[dict]:
    return json.loads((DATA / "protocols.json").read_text())


def load_resources() -> list[dict]:
    return json.loads((DATA / "resources.json").read_text())


def find_protocol(protocols: list[dict], severity: str) -> dict | None:
    for p in protocols:
        if p.get("severity") == severity:
            return p
    return None


def match_resources(resources: list[dict], category: str) -> list[dict]:
    cat = (category or "").lower()
    return [r for r in resources if cat and cat in r.get("category", "").lower()]


# --- MCP stdio server (consumed by the Bolt agent) ---
def build_server():
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("beacon-knowledge")

    @mcp.tool()
    def get_protocol(severity: str) -> dict:
        """Return the org's safeguarding protocol for a severity level
        (routine|elevated|urgent|crisis). Falls back to elevated if unknown."""
        protocols = load_protocols()
        return find_protocol(protocols, severity) or find_protocol(protocols, "elevated") or {}

    @mcp.tool()
    def find_resources(category: str) -> list[dict]:
        """Return vetted resources matching a need category
        (e.g. college-cost, college-prep, crisis, food, housing)."""
        return match_resources(load_resources(), category)

    return mcp


if __name__ == "__main__":
    build_server().run()
