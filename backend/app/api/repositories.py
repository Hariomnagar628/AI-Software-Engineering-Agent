
from fastapi import APIRouter, HTTPException

from app.schemas.repository import (
    RepositoryInspectRequest,
    RepositoryInspectResponse,
)
from app.services.repository_service import inspect_repository
from app.services.file_scanner import scan_repository
from app.schemas.repository import RepositoryScanResponse
from app.schemas.repository import (
    RepositoryFileReadRequest,
    RepositoryFileReadResponse,
)
from app.services.file_reader import read_repository_file
from app.schemas.repository import RepositoryOverviewResponse
from app.services.repository_overview import get_repository_overview
from app.schemas.repository import RepositoryStatsResponse
from app.services.repository_stats import get_repository_stats
from app.schemas.repository import RepositorySummaryResponse
from app.services.repository_summary import get_repository_summary
from app.schemas.repository import RepositoryCodeAnalysisResponse
from app.services.repository_analyzer import analyze_repository

from app.schemas.repository import (
    RepositoryImpactRequest,
    RepositoryImpactResponse,
)
from app.services.repository_analyzer import analyze_repository
from app.services.impact_analyzer import analyze_function_impact
from app.schemas.repository import (
    CodebaseSearchRequest,
    CodebaseSearchResponse,
)
from app.services.codebase_search import search_codebase
from app.schemas.repository import (
    RepositoryIndexRequest,
    RepositoryIndexResponse,
)
from app.services.repository_ingestion import index_repository
from app.core.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session
from app.schemas.repository import (
    SemanticSearchRequest,
    SemanticSearchResponse,
)

from app.services.semantic_search import search_similar_code
from app.schemas.repository import RAGRetrievalResponse
from app.services.rag_retriever import retrieve_code_context
from app.schemas.repository import (
    CodebaseQuestionRequest,
    CodebaseQuestionResponse,
)

from app.services.codebase_qa import ask_codebase_question
from app.schemas.repository import (
    RepositoryCloneRequest,
    RepositoryCloneResponse,
)

from app.services.repository_cloner import clone_repository
from app.schemas.repository import (
    RepositoryOnboardingRequest,
    RepositoryOnboardingResponse,
)

from app.services.repository_onboarding import onboard_repository
from google.genai import errors

router = APIRouter(prefix="/repositories", tags=["Repositories"])


@router.post(
    "/inspect",
    response_model=RepositoryInspectResponse,
)
def inspect_repository_endpoint(
    request: RepositoryInspectRequest,
):
    try:
        result = inspect_repository(request.path)
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc



@router.post(
    "/scan",
    response_model=RepositoryScanResponse,
)
def scan_repository_endpoint(
    request: RepositoryInspectRequest,
):
    try:
        files = scan_repository(request.path)

        return {
            "repository_path": request.path,
            "total_files": len(files),
            "files": files,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc



@router.post(
    "/read-file",
    response_model=RepositoryFileReadResponse,
)
def read_repository_file_endpoint(
    request: RepositoryFileReadRequest,
):
    try:
        return read_repository_file(
            repository_path=request.repository_path,
            relative_file_path=request.file_path,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post(
    "/overview",
    response_model=RepositoryOverviewResponse,
)
def repository_overview_endpoint(
    request: RepositoryInspectRequest,
):
    try:
        return get_repository_overview(request.path)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post(
    "/stats",
    response_model=RepositoryStatsResponse,
)
def repository_stats_endpoint(
    request: RepositoryInspectRequest,
):
    try:
        return get_repository_stats(request.path)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc




@router.post(
    "/summary",
    response_model=RepositorySummaryResponse,
)
def repository_summary_endpoint(
    request: RepositoryInspectRequest,
):
    try:
        return get_repository_summary(request.path)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc



@router.post(
    "/analyze",
    response_model=RepositoryCodeAnalysisResponse,
)
def analyze_repository_endpoint(
    request: RepositoryInspectRequest,
):
    try:
        return analyze_repository(request.path)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc



@router.post("/impact", response_model=RepositoryImpactResponse)
def get_repository_impact(request: RepositoryImpactRequest):
    try:
        analysis = analyze_repository(request.path)

        result = analyze_function_impact(
            dependency_graph=analysis["dependency_graph"],
            function_name=request.function_name,
            file_path=request.file_path,
        )

        return result

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))



@router.post("/search", response_model=CodebaseSearchResponse)
def search_repository(request: CodebaseSearchRequest):
    try:
        return search_codebase(
            repository_path=request.path,
            query=request.query,
            limit=request.limit,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )



@router.post("/index", response_model=RepositoryIndexResponse)
def index_repository_endpoint(
    request: RepositoryIndexRequest,
    db: Session = Depends(get_db),
):
    try:
        return index_repository(
            db=db,
            repository_path=request.path,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post(
    "/semantic-search",
    response_model=SemanticSearchResponse,
)
def semantic_search_endpoint(
    request: SemanticSearchRequest,
    db: Session = Depends(get_db),
):
    try:
        return search_similar_code(
            db=db,
            repository_path=request.path,
            query=request.query,
            limit=request.limit,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post("/retrieve", response_model=RAGRetrievalResponse)
def retrieve_code_endpoint(
    request: SemanticSearchRequest,
    db: Session = Depends(get_db),
):
    try:
        return retrieve_code_context(
            db=db,
            repository_path=request.path,
            query=request.query,
            limit=request.limit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post(
    "/ask",
    response_model=CodebaseQuestionResponse,
)
def ask_codebase_endpoint(
    request: CodebaseQuestionRequest,
    db: Session = Depends(get_db),
):
    try:
        return ask_codebase_question(
            db=db,
            repository_path=request.path,
            question=request.question,
            limit=request.limit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post(
    "/clone",
    response_model=RepositoryCloneResponse,
)
def clone_repository_endpoint(
    request: RepositoryCloneRequest,
):
    try:
        return clone_repository(
            repository_url=request.repository_url
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

@router.post(
    "/onboard",
    response_model=RepositoryOnboardingResponse,
)
def onboard_repository_endpoint(
    request: RepositoryOnboardingRequest,
    db: Session = Depends(get_db),
):
    try:
        return onboard_repository(
            db=db,
            repository_url=request.repository_url,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except errors.APIError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Gemini embedding service is temporarily unavailable "
                "or its quota has been exceeded. Please retry later."
            ),
        ) from exc