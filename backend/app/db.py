import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from sqlalchemy import inspect, text
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


def _migrate_run_timing_columns() -> None:
    """Add fan_out_ms / judge_ms on existing DBs (create_all does not ALTER tables).

    Works for SQLite, PostgreSQL, MySQL, and other engines SQLAlchemy inspect supports.
    """
    try:
        insp = inspect(_engine)
        cols = {c["name"] for c in insp.get_columns(Run.__tablename__)}
    except Exception:
        return

    dialect = _engine.dialect.name
    table = Run.__tablename__

    def add_integer_column(name: str) -> None:
        if dialect == "postgresql":
            stmt = text(
                f'ALTER TABLE "{table}" ADD COLUMN IF NOT EXISTS {name} INTEGER'
            )
        elif dialect in ("mysql", "mariadb"):
            stmt = text(f"ALTER TABLE `{table}` ADD COLUMN {name} INTEGER")
        else:
            stmt = text(f"ALTER TABLE {table} ADD COLUMN {name} INTEGER")

        with _engine.begin() as conn:
            conn.execute(stmt)

    if "fan_out_ms" not in cols:
        add_integer_column("fan_out_ms")
        cols.add("fan_out_ms")
    if "judge_ms" not in cols:
        add_integer_column("judge_ms")


def init_db() -> None:
    SQLModel.metadata.create_all(_engine)
    _migrate_run_timing_columns()


def get_session() -> Iterator[Session]:
    with Session(_engine) as session:
        yield session
