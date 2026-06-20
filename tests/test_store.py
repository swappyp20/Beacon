import sqlite3
from beacon.store import Store

def make_store():
    return Store(sqlite3.connect(":memory:"))

def test_add_and_get_mentee_stores_pseudonymous_handle_only():
    s = make_store()
    mid = s.add_mentee(handle="maya", mentor="U_MENTOR", channel="C_MAYA")
    m = s.get_mentee(mid)
    assert m["handle"] == "maya"
    assert m["mentor"] == "U_MENTOR"
    assert "real_name" not in m  # no PII columns exist at all

def test_followup_roundtrip_and_open_query():
    s = make_store()
    mid = s.add_mentee(handle="maya", mentor="U1", channel="C1")
    fid = s.add_followup(mentee_id=mid, raised_by="U1", summary="college fees", severity="elevated", due_at="2026-06-25")
    open_items = s.open_followups()
    assert any(f["id"] == fid and f["status"] == "open" for f in open_items)

def test_audit_event_is_append_only_with_severity_delta():
    s = make_store()
    s.log_audit(actor="U1", action="escalate", target="maya", severity_before="elevated", severity_after="urgent", payload="{}")
    rows = s.audit_for_target("maya")
    assert rows[0]["action"] == "escalate"
    assert rows[0]["severity_before"] == "elevated"
    assert rows[0]["severity_after"] == "urgent"
