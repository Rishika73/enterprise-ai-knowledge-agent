from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from rag import generate_answer

app = FastAPI(
    title="Enterprise AI Knowledge Agent",
    version="1.0.0"
)


class QueryRequest(BaseModel):
    question: str
    file_path: str = "data/sample_document.txt"
    top_k: int = 3


@app.get("/")
def root():
    return {
        "message": "Enterprise AI Knowledge Agent API is running."
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/ask")
def ask_question(request: QueryRequest):
    try:
        result = generate_answer(
            query=request.question,
            file_path=request.file_path,
            top_k=request.top_k
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )
