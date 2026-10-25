from pydantic import BaseModel, Field

class DebateCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    transcript: str = Field(min_length=1)

class DebateSummary(BaseModel):
    id: int
    title: str
    status: str
    winner: str | None = None
    created_at: str

class DebateResult(BaseModel):
    id: int
    title: str
    status: str
    result: dict | None
