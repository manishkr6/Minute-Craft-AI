# MinuteCraftAI FastAPI Backend (Render Ready)

## Structure
- `backend/core/` and `backend/utils/`: your existing RAG logic (unchanged)
- `backend/app/`: new FastAPI wrapper layer
- `backend/requirements-api.txt`: API/runtime deps for deployment
- `render.yaml`: Render service definition

## API Endpoints
- `GET /` basic API message
- `GET /v1/health` health check
- `POST /v1/process` run pipeline and start RAG session
- `POST /v1/ask` ask question using `session_id`

## Local Run
```bash
cd backend
pip install -r requirements-api.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Render Setup
1. Push this repository to GitHub.
2. In Render, create a new Blueprint and point to this repo.
3. Render will read `render.yaml`.
4. Set secret env vars in Render dashboard:
   - `MISTRAL_API_KEY`
   - `SARVAM_API_KEY` (needed only for `hinglish` mode)

## Example Requests
### Process source
```bash
curl -X POST http://localhost:8000/v1/process \
  -H "Content-Type: application/json" \
  -d '{"source":"https://www.youtube.com/watch?v=xxxx","language":"english"}'
```

### Ask follow-up question
```bash
curl -X POST http://localhost:8000/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"session_id":"<SESSION_ID_FROM_PROCESS>","question":"What are the action items?"}'
```
