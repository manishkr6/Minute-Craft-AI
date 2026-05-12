from fastapi import APIRouter, HTTPException

from app.models.schemas import AskRequest, AskResponse, HealthResponse, ProcessRequest, ProcessResponse
from app.services.pipeline_service import pipeline_service

router = APIRouter(prefix="/v1", tags=["rag"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/process", response_model=ProcessResponse)
def process(req: ProcessRequest) -> ProcessResponse:
    try:
        data = pipeline_service.process(source=req.source, language=req.language)
        return ProcessResponse(**data)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    try:
        answer = pipeline_service.ask(session_id=req.session_id, question=req.question)
        return AskResponse(answer=answer)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
