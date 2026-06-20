from slack_bolt import App, Assistant
from slack_bolt.adapter.socket_mode import SocketModeHandler

from .config import config
from .store import Store
from .llm import LLM
from .mcp_client import KnowledgeClient
from .rts import RTSClient
from .triage import run_triage
from .blocks import triage_card, resource_cards
from .resources import navigate_resources, handoff_text
from .scorecard import synthesize_card, render_canvas_markdown
from .home import home_view
from mcp_server.server import load_resources


def create_app() -> App:
    """Construct the Bolt app and all dependencies, registering every handler.
    Kept as a factory so importing this module spawns nothing (no MCP subprocess,
    no Slack auth) — construction happens only when create_app()/main() runs."""
    app = App(token=config.bot_token)
    store = Store.open(config.db_path)
    llm = LLM()
    knowledge = KnowledgeClient.connect_stdio(config.mcp_cmd)
    rts = RTSClient(token=config.bot_token, scope_channels=config.rts_scope_channels,
                    use_fallback=not config.rts_scope_channels)

    assistant = Assistant()

    @assistant.thread_started
    def greet(say, set_suggested_prompts):
        say("Hi — describe a mentee concern and I'll triage it, ground it in your "
            "protocol, and help you route it. I never talk to kids and I don't diagnose.")
        set_suggested_prompts(prompts=[
            {"title": "Triage a concern",
             "message": "Met Maya today — stressed about college app fees and she seemed really down."},
        ])

    @assistant.user_message
    def on_message(payload, set_status, say, client, context):
        set_status("Reviewing and checking the protocol…")  # avoids a silent hang
        text = payload.get("text", "")
        mentor = context.get("user_id", "unknown")

        # Scorecard intent (Pillar 6): draft for mentor approval before saving a Canvas.
        if "scorecard" in text.lower():
            handle = (text.lower().split("scorecard")[0].strip().split() or ["this mentee"])[-1]
            card = synthesize_card(handle, rts.recall(handle, limit=8), store.open_followups(), llm=llm)
            say(text="Draft scorecard (review before I save it):\n```" + render_canvas_markdown(handle, card) + "```",
                blocks=[{"type": "actions", "elements": [
                    {"type": "button", "style": "primary",
                     "text": {"type": "plain_text", "text": "Approve & save to Canvas"},
                     "action_id": "approve_scorecard", "value": handle}]}])
            return

        result = run_triage(text, mentor=mentor, llm=llm, knowledge=knowledge, rts=rts)

        # Persist follow-up + audit (every sensitive action is logged, spec §6).
        if result.handle:
            m = store.find_mentee_by_handle(result.handle) or {
                "id": store.add_mentee(result.handle, mentor, payload.get("channel", ""))}
            store.add_followup(m["id"], mentor, ", ".join(result.needs) or "wellbeing concern", result.severity, None)
        store.log_audit(actor=mentor, action="triage", target=result.handle or "unknown",
                        severity_after=result.severity, payload=text[:500])

        say(blocks=triage_card(result), text=f"Triage: {result.severity}")
        if result.needs_clarification:
            say("Which mentee is this about? I won't assume.")
        if result.needs:
            res = navigate_resources(text, llm=llm, knowledge=knowledge)
            say(blocks=resource_cards(res), text="Resources")
            store.log_audit(actor=mentor, action="resources_shown", target=result.handle or "unknown",
                            payload=",".join(r["id"] for r in res))

    @app.action("route_concern")
    def route_concern(ack, body, client):
        ack()
        handle = body["actions"][0]["value"]
        mentor = body["user"]["id"]
        client.chat_postMessage(channel=config.safeguarding_channel,
            text=f":handshake: *{mentor}* routed a concern about *{handle}* for review.")
        store.log_audit(actor=mentor, action="escalate", target=handle, severity_after="routed")
        client.chat_postMessage(channel=body["channel"]["id"], text="Routed to @safeguarding-leads and logged.")

    @app.action("route_crisis")
    def route_crisis(ack, body, client):
        ack()
        handle = body["actions"][0]["value"]
        mentor = body["user"]["id"]
        client.chat_postMessage(channel=config.safeguarding_channel,
            text=f":rotating_light: *CRISIS* flagged by *{mentor}* re *{handle}* — on-call lead needed NOW.")
        store.log_audit(actor=mentor, action="escalate_crisis", target=handle, severity_after="crisis")

    @app.action("resource_handoff")
    def resource_handoff(ack, body, client):
        ack()
        rid = body["actions"][0]["value"]
        match = next((x for x in load_resources() if x["id"] == rid), None)
        if match:
            client.chat_postMessage(channel=body["channel"]["id"],
                text="Hand this to the mentee/family:\n" + handoff_text(match))
            store.log_audit(actor=body["user"]["id"], action="resource_shared", target=rid)

    @app.action("view_protocol")
    def view_protocol(ack):
        ack()

    @app.action("approve_scorecard")
    def approve_scorecard(ack, body, client):
        ack()
        handle = body["actions"][0]["value"]
        card = synthesize_card(handle, rts.recall(handle, limit=8), store.open_followups(), llm=llm)
        md = render_canvas_markdown(handle, card)
        canvas = client.canvases_create(title=f"{handle} — Progress Snapshot",
                                        document_content={"type": "markdown", "markdown": md})
        store.log_audit(actor=body["user"]["id"], action="scorecard_approved", target=handle,
                        payload=canvas.get("canvas_id", ""))
        client.chat_postMessage(channel=body["channel"]["id"],
            text=f"Approved. Saved *{handle}*'s snapshot to a Canvas.")

    @app.event("app_home_opened")
    def render_home(event, client):
        client.views_publish(user_id=event["user"], view=home_view(store.open_followups()))

    app.assistant(assistant)
    return app


def main():
    import truststore
    truststore.inject_into_ssl()  # use the OS trust store (works behind TLS-inspecting proxies)
    SocketModeHandler(create_app(), config.app_token).start()


if __name__ == "__main__":
    main()
