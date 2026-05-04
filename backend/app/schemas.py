from datetime import datetime
from pydantic import BaseModel, Field


class TimingStage(BaseModel):
    """Named segment of wall-clock time inside one downstream operation."""

    stage: str
    ms: int


class Citation(BaseModel):
    url: str
    title: str | None = None
    snippet: str | None = None


class ProviderResult(BaseModel):
    provider: str
    grounded: bool
    model: str
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    latency_ms: int
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None
    raw: dict = Field(default_factory=dict)
    error: str | None = None
    timings: list[TimingStage] = Field(default_factory=list)


class JudgeScore(BaseModel):
    correctness: int
    groundedness: int
    citation_support: int
    rationale: str
    judge_provider: str | None = None  # "google" | "anthropic"
    judge_model: str | None = None
    latency_ms: int | None = None
    timings: list[TimingStage] = Field(default_factory=list)


class ProviderCallOut(ProviderResult):
    id: int
    judge: JudgeScore | None = None


class RunOut(BaseModel):
    id: int
    query: str
    created_at: datetime
    calls: list[ProviderCallOut]
    fan_out_ms: int | None = Field(
        default=None,
        description="Wall-clock time for parallel provider fan-out in POST /api/query.",
    )
    judge_ms: int | None = Field(
        default=None,
        description="Wall-clock time for LLM-as-judge over all provider results.",
    )


class QueryRequest(BaseModel):
    query: str
    providers: list[str]
    include_ungrounded: bool = True
    run_judge: bool = True
    judge_provider: str | None = None  # "google" | "anthropic" | None (use default)
