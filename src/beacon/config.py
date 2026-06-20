import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Config:
    bot_token: str = os.getenv("SLACK_BOT_TOKEN", "")
    app_token: str = os.getenv("SLACK_APP_TOKEN", "")
    anthropic_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    model_reason: str = os.getenv("ANTHROPIC_MODEL_REASON", "claude-opus-4-8")
    model_classify: str = os.getenv("ANTHROPIC_MODEL_CLASSIFY", "claude-haiku-4-5")
    mcp_cmd: str = os.getenv("BEACON_MCP_CMD", "python mcp_server/server.py")
    safeguarding_channel: str = os.getenv("CHANNEL_SAFEGUARDING", "#safeguarding-leads")
    rts_scope_channels: tuple = tuple(
        c.strip() for c in os.getenv("RTS_SCOPE_CHANNELS", "").split(",") if c.strip()
    )
    db_path: str = os.getenv("BEACON_DB", "beacon.db")

config = Config()
