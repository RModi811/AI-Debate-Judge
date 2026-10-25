


"""Regression tests for transcript attribution and clash display."""

import ast
from pathlib import Path

import pytest

from app.services import judge_pipeline


@pytest.fixture
def sample_transcript():
    return """
[PRO CONSTRUCTIVE — MAYA CHEN]
A public transport investment reduces congestion and improves access to employment opportunities across the city.

[CON CONSTRUCTIVE — AISHA PATEL]
The proposed transport investment requires substantial public funding that could otherwise support essential healthcare services.

[PRO REBUTTAL — DANIEL BROOKS]
Improved public transport creates long-term economic benefits by connecting workers with jobs and reducing dependence on private vehicles.

[CON REBUTTAL — LUCAS REED]
Without reliable maintenance funding, the proposed infrastructure may deteriorate and fail to deliver its promised benefits.

[CROSSFIRE — MAYA CHEN AND AISHA PATEL]
How would you guarantee that the maintenance budget remains available throughout the project's lifetime?
"""


def test_explicit_pro_and_con_speaker_labels(sample_transcript):
    labels = judge_pipeline._infer_speaker_labels(sample_transcript)

    assert set(labels["A"]) == {"MAYA CHEN", "DANIEL BROOKS"}
    assert set(labels["B"]) == {"AISHA PATEL", "LUCAS REED"}


def test_transcript_segments_have_unique_ids_and_crossfire(sample_transcript):
    parsed = judge_pipeline._extract_transcript_segments(sample_transcript)[0]
    segments = parsed["segments"]

    ids = [segment["turn_id"] for segment in segments]

    assert len(ids) == len(set(ids))
    assert len(segments) == 5
    assert any(segment["is_crossfire"] for segment in segments)


@pytest.mark.parametrize(
    ("side", "expected_speaker"),
    [("A", "A"), ("B", "B")],
)
def test_source_quote_corrects_side_and_turn_id(
    sample_transcript, side, expected_speaker
):
    parsed = judge_pipeline._extract_transcript_segments(sample_transcript)[0]
    segment = next(
        item for item in parsed["segments"]
        if item["side"] == side and not item["is_crossfire"]
    )

    quote = " ".join(segment["text"].split()[:10])
    argument = {
        "source_spans": [quote],
        "speaker": "WRONG",
        "turn_id": "T1",
    }

    kept = judge_pipeline._attribute_argument_from_source(argument, parsed)

    assert kept is True
    assert argument["speaker"] == expected_speaker
    assert argument["turn_id"] == segment["turn_id"]


def test_crossfire_only_source_quote_is_rejected(sample_transcript):
    parsed = judge_pipeline._extract_transcript_segments(sample_transcript)[0]
    segment = next(item for item in parsed["segments"] if item["is_crossfire"])

    quote = " ".join(segment["text"].split()[:10])
    argument = {
        "source_spans": [quote],
        "speaker": "A",
        "turn_id": "T1",
    }

    assert judge_pipeline._attribute_argument_from_source(argument, parsed) is False


def test_clash_display_joins_by_id_and_preserves_missing_findings():
    ui_path = Path(__file__).resolve().parents[1] / "ui" / "streamlit_app.py"
    tree = ast.parse(ui_path.read_text(encoding="utf-8"), filename=str(ui_path))

    helper_node = next(
        (
            node for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "_clash_display_rows"
        ),
        None,
    )

    assert helper_node is not None, "_clash_display_rows helper not found"

    module = ast.Module(body=[helper_node], type_ignores=[])
    namespace = {}
    exec(compile(module, str(ui_path), "exec"), namespace)

    rows = namespace["_clash_display_rows"](
        {
            "clash_results": [
                {
                    "clash_id": "C1",
                    "finding": "PRO wins this clash",
                    "decisive": True,
                }
            ]
        },
        {
            "clashes": [
                {
                    "clash_id": "C1",
                    "issue": "Privacy",
                    "description": "Data misuse risk",
                },
                {
                    "clash_id": "C2",
                    "issue": "Accuracy",
                    "description": "False matches",
                },
            ]
        },
    )

    by_id = {row["clash_id"]: row for row in rows}

    assert by_id["C1"]["finding"] == "PRO wins this clash"
    assert by_id["C2"]["description"] == "False matches"
    assert by_id["C2"]["finding"] == ""
