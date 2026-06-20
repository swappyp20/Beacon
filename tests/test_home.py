from beacon.home import home_view


def test_home_shows_open_followups_and_safety_footer():
    v = home_view([{"mentee_id": 1, "summary": "college fees", "severity": "elevated"}])
    flat = str(v)
    assert v["type"] == "home"
    assert "1 follow-up" in flat
    assert "college fees" in flat
    assert "never talks to kids" in flat


def test_home_empty_state_says_nothing_dropped():
    flat = str(home_view([]))
    assert "Nothing dropped" in flat
