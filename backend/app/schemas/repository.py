from pydantic import BaseModel, Field

class RepositoryInspectRequest(BaseModel):
    path: str


class RepositoryInspectResponse(BaseModel):
    name: str
    root_path: str
    branch: str | None
    is_dirty: bool


class RepositoryScanResponse(BaseModel):
    repository_path: str
    total_files: int
    files: list[str]


class RepositoryFileReadRequest(BaseModel):
    repository_path: str
    file_path: str


class RepositoryFileReadResponse(BaseModel):
    path: str
    content: str
    size_bytes: int


class RepositoryOverviewData(BaseModel):
    name: str
    root_path: str
    branch: str | None
    is_dirty: bool


class RepositoryOverviewResponse(BaseModel):
    repository: RepositoryOverviewData
    total_files: int
    files: list[str]


class RepositoryStatsResponse(BaseModel):
    total_files: int
    extension_counts: dict[str, int]


class RepositorySummaryResponse(BaseModel):
    repository: RepositoryOverviewData
    total_files: int
    files: list[str]
    statistics: dict[str, int]



class CodeAnalysisError(BaseModel):
    file_path: str
    error: str


class RepositoryCodeAnalysisResponse(BaseModel):
    repository_path: str
    python_files_found: int
    files_analyzed: int
    analyzed_files: list[str]
    classes: list[dict]
    functions: list[dict]
    imports: list[dict]
    errors: list[CodeAnalysisError]
    calls: list[dict]
    resolved_calls: list[dict]
    file_dependency_graph: dict
    unified_graph: dict

class RepositoryImpactRequest(BaseModel):
    path: str
    function_name: str
    file_path: str | None = None


class RepositoryImpactResponse(BaseModel):
    target: dict
    direct_callers: list[dict]
    indirect_callers: list[dict]
    total_affected_functions: int

class CodebaseSearchRequest(BaseModel):
    path: str
    query: str
    limit: int = Field(default=10, ge=1, le=50)


class CodebaseSearchResult(BaseModel):
    file_path: str
    score: int
    matched_terms: list[str]
    matching_lines: list[dict]


class CodebaseSearchResponse(BaseModel):
    query: str
    total_files_searched: int
    total_matching_files: int
    results: list[CodebaseSearchResult]


class RepositoryIndexRequest(BaseModel):
    path: str


class RepositoryIndexResponse(BaseModel):
    repository_path: str
    total_files: int
    total_chunks: int
    inserted: int
    skipped: int
    errors: list[dict]


class SemanticSearchRequest(BaseModel):
    path: str
    query: str
    limit: int = Field(default=5, ge=1, le=50)


class SemanticSearchResult(BaseModel):
    chunk_id: str
    file_path: str
    language: str
    start_line: int
    end_line: int
    content: str
    similarity_score: float
    metadata: dict


class SemanticSearchResponse(BaseModel):
    repository_path: str
    query: str
    total_results: int
    results: list[SemanticSearchResult]


class RAGSource(BaseModel):
    source_id: str
    chunk_id: str
    file_path: str
    start_line: int
    end_line: int
    similarity_score: float


class RAGRetrievalResponse(BaseModel):
    repository_path: str
    query: str
    total_retrieved: int
    total_sources: int
    retrieved_chunks: list[SemanticSearchResult]
    context: str
    sources: list[RAGSource]


class CodebaseQuestionRequest(BaseModel):
    path: str
    question: str
    limit: int = Field(default=5, ge=1, le=50)


class CodebaseQuestionResponse(BaseModel):
    repository_path: str
    question: str
    answer: str
    sources: list[RAGSource]
    total_sources: int

class RepositoryCloneRequest(BaseModel):
    repository_url: str


class RepositoryCloneResponse(BaseModel):
    repository_name: str
    repository_url: str
    repository_path: str
    status: str

class RepositoryOnboardingRequest(BaseModel):
    repository_url: str


class RepositoryOnboardingResponse(BaseModel):
    repository_name: str
    repository_url: str
    repository_path: str
    clone_status: str
    branch: str | None
    total_files: int
    total_chunks: int
    inserted_chunks: int
    skipped_chunks: int
    indexing_errors: list[dict]
    status: str