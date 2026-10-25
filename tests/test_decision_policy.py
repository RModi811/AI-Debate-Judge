from app.services.judge_pipeline import _apply_decision_consistency_policy


def _decision(status="unresolved", a=8.0, b=7.0):
    scores = {
        "A": {key: a for key in ("reasoning", "clash", "weighing", "clarity", "strategy", "persuasion")},
        "B": {key: b for key in ("reasoning", "clash", "weighing", "clarity", "strategy", "persuasion")},
    }
    return {
        "decision_status": status,
        "winner": "UNRESOLVED" if status == "unresolved" else "A",
        "confidence": "medium",
        "scores": scores,
        "limitations": [],
        "explanation_points": [],
    }


def _analysis(a_count=3, b_count=3):
    return {
        "arguments": (
            [{"speaker": "A"} for _ in range(a_count)]
            + [{"speaker": "B"} for _ in range(b_count)]
        )
    }


def test_material_score_gap_resolves_unjustified_abstention():
    decision = _apply_decision_consistency_policy(_decision(a=8.0, b=7.0), _analysis())
    assert decision["decision_status"] == "resolved"
    assert decision["winner"] == "A"
    assert decision["resolution_method"] == "weighted_score_gap_fallback"
    assert any("score-based fallback" in item for item in decision["limitations"])


def test_near_tie_remains_unresolved():
    decision = _decision(a=8.0, b=8.0)
    decision["scores"]["B"]["persuasion"] = 7
    decision = _apply_decision_consistency_policy(decision, _analysis())
    assert decision["decision_status"] == "unresolved"
    assert decision["winner"] == "UNRESOLVED"


def test_insufficient_arguments_do_not_trigger_fallback():
    decision = _apply_decision_consistency_policy(_decision(a=8.0, b=7.0), _analysis(a_count=1))
    assert decision["decision_status"] == "unresolved"


def test_existing_resolved_decision_is_not_overwritten():
    decision = _apply_decision_consistency_policy(_decision(status="resolved", a=7.0, b=8.0), _analysis())
    assert decision["winner"] == "A"
