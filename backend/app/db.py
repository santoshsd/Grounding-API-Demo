import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from sqlmodel import Field, Session, SQLModel, create_engine, Relationship

from .config import get_settings


class Run(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    query: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    fan_out_ms: int | None = None
    judge_ms: int | None = None
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


def _make_engine():
    url = get_settings().database_url
    if url.startswith("sqlite:///"):
        db_path = Path(url.replace("sqlite:///", "", 1))
        db_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(
        url,
        echo=False,
        connect_args={"check_same_thread": False} if url.startswith("sqlite") else {},
    )

_engine = _make_engine()


def _sqlite_file_path() -> Path | None:
    url = get_settings().database_url
    if not url.startswith("sqlite:///"):
        return None
    return Path(url.replace("sqlite:///", "", 1))


def _migrate_sqlite_timing_columns() -> None:
    """Add timing columns on existing SQLite DBs (create_all does not ALTER)."""
    path = _sqlite_file_path()
    if path is None:
        return
    import sqlite3

    conn = sqlite3.connect(str(path))
    try:
        cur = conn.execute("PRAGMA table_info(run)")
        cols = {row[1] for row in cur.fetchall()}
        if "fan_out_ms" not in cols:
            conn.execute("ALTER TABLE run ADD COLUMN fan_out_ms INTEGER")
        if "judge_ms" not in cols:
            conn.execute("ALTER TABLE run ADD COLUMN judge_ms INTEGER")
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    SQLModel.metadata.create_all(_engine)
    _migrate_sqlite_timing_columns()


def get_session() -> Iterator[Session]:
    with Session(_engine) as session:
        yield session
