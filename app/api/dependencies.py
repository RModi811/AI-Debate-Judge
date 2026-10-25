from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User

def current_user(x_user_id: int | None = Header(default=None), db: Session = Depends(get_db)):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Login required")
    user = db.get(User, x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user
