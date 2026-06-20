"""Seed the BrightPath Mentors sandbox: create channels and post prior history
so RTS has real institutional memory to find. Idempotent-ish: reuses a channel
if it already exists. Run once against a fresh dev workspace.

Requires SLACK_BOT_TOKEN in .env with scopes: channels:manage, channels:read,
chat:write. Usage: python seed/seed_sandbox.py
"""
import json
from pathlib import Path
from slack_sdk import WebClient
from beacon.config import config


def main():
    client = WebClient(token=config.bot_token)
    data = json.loads((Path(__file__).parent / "brightpath.json").read_text())
    ids = {}
    for name in data["channels"]:
        try:
            resp = client.conversations_create(name=name)
            ids[name] = resp["channel"]["id"]
        except Exception:
            found = next((c for c in client.conversations_list(limit=200)["channels"] if c["name"] == name), None)
            if found:
                ids[name] = found["id"]
    for chan, msgs in data["messages"].items():
        cid = ids.get(chan)
        if not cid:
            continue
        for text in msgs:
            client.chat_postMessage(channel=cid, text=text)
    print("Seeded channels:", ids)
    wanted = [c for c in ["mentee-maya", "mentee-jordan", "safeguarding-leads"] if c in ids]
    print("Set RTS_SCOPE_CHANNELS to:", ",".join(ids[c] for c in wanted))


if __name__ == "__main__":
    main()
