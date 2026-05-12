from __future__ import annotations

import threading
import uuid
from typing import Any

from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import ask_question, build_rag_chain
from core.summarizer import generate_title, summarize
from core.transcriber import transcribe_all
from utils.audio_processor import process_input


class PipelineService:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._rag_sessions: dict[str, Any] = {}

    def process(self, source: str, language: str) -> dict[str, str]:
        chunks = process_input(source)
        transcript = transcribe_all(chunks, language=language)

        title = generate_title(transcript)
        summary = summarize(transcript)
        action_item = extract_action_items(transcript)
        key_decisions = extract_key_decisions(transcript)
        open_questions = extract_questions(transcript)

        rag_chain = build_rag_chain(transcript)
        session_id = str(uuid.uuid4())

        with self._lock:
            self._rag_sessions[session_id] = rag_chain

        return {
            "session_id": session_id,
            "title": title,
            "transcript": transcript,
            "summary": summary,
            "action_item": action_item,
            "key_decisions": key_decisions,
            "open_questions": open_questions,
        }

    def ask(self, session_id: str, question: str) -> str:
        with self._lock:
            rag_chain = self._rag_sessions.get(session_id)

        if rag_chain is None:
            raise KeyError("Invalid session_id. Run /v1/process first.")

        return ask_question(rag_chain, question)


pipeline_service = PipelineService()
