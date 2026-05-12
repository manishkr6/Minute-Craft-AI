from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.routes import router

load_dotenv()

app = FastAPI(
    title="MinuteCraftAI Backend",
    version="1.0.0",
    description="FastAPI wrapper for the existing RAG pipeline",
)

app.include_router(router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "MinuteCraftAI API is running"}
