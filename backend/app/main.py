
from fastapi import FastAPI

from app.api.repositories import router as repositories_router

app = FastAPI(
    title="AI Software Engineering Agent",
    description="An AI agent that understands codebases, investigates bugs, and proposes verified fixes.",
    version="0.1.0",
)

app.include_router(repositories_router)


@app.get("/")
def home():
    return {
        "message": "AI Software Engineering Agent is running!",
        "status": "healthy",
    }
