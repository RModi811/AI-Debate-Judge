from fastapi import FastAPI
from app.db.database import init_db
from app.api.routes import auth, debates

app = FastAPI(title="AI Debate Judge API", version="0.2.0")
init_db()
app.include_router(auth.router)
app.include_router(debates.router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "ai-debate-judge-api"}
