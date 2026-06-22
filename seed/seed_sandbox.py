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
    import truststore
    truststore.inject_into_ssl()  # OS trust store (works behind TLS-inspecting proxies)
    client = WebClient(token=config.bot_token)
    data = json.loads((Path(__file__).parent / "brightpath.json").read_text())
    ids, created = {}, set()
    for name in data["channels"]:
        try:
            resp = client.conversations_create(name=name)
            ids[name] = resp["channel"]["id"]
            created.add(name)
        except Exception:
            found = next((c for c in client.conversations_list(
                limit=200, types="public_channel")["channels"] if c["name"] == name), None)
            if found:
                ids[name] = found["id"]
    # The bot must be a member to post; best-effort join (needs channels:join scope).
    for cid in ids.values():
        try:
            client.conversations_join(channel=cid)
        except Exception:
            pass
    # Only seed channels freshly created this run, so re-runs don't duplicate history.
    posted = 0
    for chan, msgs in data["messages"].items():
        cid = ids.get(chan)
        if not cid or chan not in created:
            continue
        for text in msgs:
            try:
                client.chat_postMessage(channel=cid, text=text)
                posted += 1
            except Exception as e:
                print(f"  skip ({chan}): {e}")
    print(f"Posted {posted} new message(s). Channels: {ids}")
    wanted = [c for c in ["mentee-maya", "mentee-jordan", "safeguarding-leads"] if c in ids]
    print("Set RTS_SCOPE_CHANNELS to:", ",".join(ids[c] for c in wanted))


if __name__ == "__main__":
    main()
