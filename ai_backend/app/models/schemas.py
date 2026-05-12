from pydantic import BaseModel, Field


class ProcessRequest(BaseModel):
    source: str = Field(..., description="YouTube URL or local file path")
    language: str = Field(default="english", pattern="^(english|hinglish)$")


class ProcessResponse(BaseModel):
    session_id: str
    title: str
    transcript: str
    summary: str
    action_item: str
    key_decisions: str
    open_questions: str


class AskRequest(BaseModel):
    session_id: str
    question: str = Field(..., min_length=1)


class AskResponse(BaseModel):
    answer: str


class HealthResponse(BaseModel):
    status: str
