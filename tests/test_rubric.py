from beacon.rubric import SEVERITIES, default_rubric, resolve_rubric


def test_severities_are_ordered_low_to_high():
    assert SEVERITIES == ["routine", "elevated", "urgent", "crisis"]


def test_default_rubric_has_every_level():
    rb = default_rubric()
    assert set(rb) == set(SEVERITIES)


def test_resolve_prefers_mcp_when_present_else_default():
    mcp_rubric = {"elevated": "org-specific elevated definition"}
    merged = resolve_rubric(mcp_rubric)
    assert merged["elevated"] == "org-specific elevated definition"
    assert "crisis" in merged  # default fills the gap
