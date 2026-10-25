import pytest

from app.llm.json_validator import parse_json


def test_parse_plain_json():
    assert parse_json('{"ok": true}') == {"ok": True}


def test_parse_fenced_json():
    assert parse_json('```json\n{"ok": true}\n```') == {"ok": True}


def test_invalid_json_has_actionable_error():
    with pytest.raises(ValueError, match="invalid or incomplete JSON"):
        parse_json('{"ok":')
