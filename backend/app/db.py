import json
from datetime import datetime, timezone
from typing import Iterator

from sqlmodel import Field, Session, SQLModel, create_engine, Relationship

from .config import get_settings


class Run(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    query: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    calls: list["ProviderCall"] = Relationship(back_populates="run")


class ProviderCall(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="run.id", index=True)
    provider: str
    grounded: bool
    model: str
    answer: str
    citations_json: str = "[]"
    latency_ms: int
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None
    raw_json: str = "{}"
    error: str | None = None

    run: Run | None = Relationship(back_populates="calls")
    judge: "JudgeRow" = Relationship(  # type: ignore[assignment]
        back_populates="call",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"},
    )

    @property
    def citations(self) -> list[dict]:
        return json.loads(self.citations_json)


class JudgeRow(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    call_id: int = Field(foreign_key="providercall.id", index=True, unique=True)
    correctness: int
    groundedness: int
    citation_support: int
    rationale: str
    judge_provider: str | None = None
    judge_model: str | None = None

    call: ProviderCall | None = Relationship(back_populates="judge")


_engine = create_engine(
    get_settings().database_url,
    echo=False,
    connect_args={"check_same_thread": False}
    if get_settings().database_url.startswith("sqlite")
    else {},
)


def init_db() -> None:
    SQLModel.metadata.create_all(_engine)


def get_session() -> Iterator[Session]:
    with Session(_engine) as session:
        yield session
