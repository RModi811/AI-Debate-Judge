
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.debate import Debate
from app.schemas.debate import DebateCreate
from app.api.dependencies import current_user
from app.services.judge_pipeline import analyze_debate
from app.config import MODEL_CONFIG, RUBRIC


router = APIRouter(prefix="/debates", tags=["debates"])


@router.get("")
def history(
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Debate)
        .filter(Debate.user_id == user.id)
        .order_by(Debate.created_at.desc())
        .all()
    )

    return [
        {
            "id": d.id,
            "title": d.title,
            "status": d.status,
            "winner": (d.result or {}).get("decision", {}).get("winner"),
            "created_at": d.created_at.isoformat(),
        }
        for d in rows
    ]


@router.get("/{debate_id}")
def get_debate(
    debate_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    d = (
        db.query(Debate)
        .filter(
            Debate.id == debate_id,
            Debate.user_id == user.id,
        )
        .first()
    )

    if not d:
        raise HTTPException(status_code=404, detail="Debate not found")

    return {
        "id": d.id,
        "title": d.title,
        "status": d.status,
        "result": d.result,
        "transcript": d.transcript,
    }


@router.post("")
async def create_debate(
    req: DebateCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    d = Debate(
        user_id=user.id,
        title=req.title,
        transcript=req.transcript,
        status="analyzing",
        model_version=MODEL_CONFIG["model"],
        rubric_version=RUBRIC["version"],
    )

    db.add(d)
    db.commit()
    db.refresh(d)

    try:
        result = await analyze_debate(req.transcript)

        d.result = result
        d.status = result["decision"]["decision_status"]

        db.commit()
        db.refresh(d)

    except Exception as exc:
        d.status = "failed"
        d.result = {"error": str(exc)}
        db.commit()

        raise HTTPException(
            status_code=502,
            detail=f"Local judge failed: {exc}",
        )

    return {
        "id": d.id,
        "title": d.title,
        "status": d.status,
        "result": d.result,
    }


@router.delete("/{debate_id}")
def delete_debate(
    debate_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    d = (
        db.query(Debate)
        .filter(
            Debate.id == debate_id,
            Debate.user_id == user.id,
        )
        .first()
    )

    if not d:
        raise HTTPException(status_code=404, detail="Debate not found")

    db.delete(d)
    db.commit()

    return {
        "deleted": True,
        "id": debate_id,
        "message": "Debate deleted successfully",
    }
