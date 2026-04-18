import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from . import judge as judge_mod
from .config import PROVIDERS, get_settings
from .db import JudgeRow, ProviderCall, Run, get_session, init_db
from .runner import fan_out
from .schemas import (
    Citation,
    JudgeScore,
    ProviderCallOut,
    ProviderResult,
    QueryRequest,
    RunOut,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Grounding API Sample", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in get_settings().cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _call_to_out(call: ProviderCall) -> ProviderCallOut:
    judge = None
    if call.judge:
        judge = JudgeScore(
            correctness=call.judge.correctness,
            groundedness=call.judge.groundedness,
            citation_support=call.judge.citation_support,
            rationale=call.judge.rationale,
            judge_provider=call.judge.judge_provider,
            judge_model=call.judge.judge_model,
        )
    return ProviderCallOut(
        id=call.id or 0,
        provider=call.provider,
        grounded=call.grounded,
        model=call.model,
        answer=call.answer,
        citations=[Citation(**c) for c in json.loads(call.citations_json)],
        latency_ms=call.latency_ms,
        input_tokens=call.input_tokens,
        output_tokens=call.output_tokens,
        cost_usd=call.cost_usd,
        raw=json.loads(call.raw_json),
        error=call.error,
        judge=judge,
    )


def _run_to_out(run: Run) -> RunOut:
    return RunOut(
        id=run.id or 0,
        query=run.query,
        created_at=run.created_at,
        calls=[_call_to_out(c) for c in run.calls],
    )


@app.get("/api/providers")
def list_providers() -> list[str]:
    return PROVIDERS


@app.get("/api/judge-config")
def judge_config() -> dict:
    s = get_settings()
    return {
        "default": s.judge_provider,
        "options": [
            {
                "id": "google",
                "label": "Gemini",
                "model": s.judge_model_google,
                "available": bool(s.google_api_key),
            },
            {
                "id": "anthropic",
                "label": "Claude",
                "model": s.judge_model_anthropic,
                "available": bool(s.anthropic_api_key),
            },
        ],
    }


@app.post("/api/query", response_model=RunOut)
async def run_query(
    req: QueryRequest, session: Session = Depends(get_session)
) -> RunOut:
    if not req.query.strip():
        raise HTTPException(400, "query is required")

    results: list[ProviderResult] = await fan_out(
        req.query, req.providers, req.include_ungrounded
    )

    run = Run(query=req.query)
    session.add(run)
    session.commit()
    session.refresh(run)

    calls: list[ProviderCall] = []
    for r in results:
        call = ProviderCall(
            run_id=run.id,  # type: ignore[arg-type]
            provider=r.provider,
            grounded=r.grounded,
            model=r.model,
            answer=r.answer,
            citations_json=json.dumps([c.model_dump() for c in r.citations]),
            latency_ms=r.latency_ms,
            input_tokens=r.input_tokens,
            output_tokens=r.output_tokens,
            cost_usd=r.cost_usd,
            raw_json=json.dumps(r.raw, default=str),
            error=r.error,
        )
        session.add(call)
        calls.append(call)
    session.commit()
    for c in calls:
        session.refresh(c)

    if req.run_judge:
        scores = await asyncio.gather(
            *(judge_mod.score(req.query, r, req.judge_provider) for r in results)
        )
        for call, score in zip(calls, scores, strict=True):
            if score is None:
                continue
            session.add(
                JudgeRow(
                    call_id=call.id,  # type: ignore[arg-type]
                    correctness=score.correctness,
                    groundedness=score.groundedness,
                    citation_support=score.citation_support,
                    rationale=score.rationale,
                    judge_provider=score.judge_provider,
                    judge_model=score.judge_model,
                )
            )
        session.commit()

    session.refresh(run)
    return _run_to_out(run)


@app.get("/api/runs", response_model=list[RunOut])
def list_runs(session: Session = Depends(get_session)) -> list[RunOut]:
    runs = session.exec(select(Run).order_by(Run.created_at.desc())).all()
    return [_run_to_out(r) for r in runs]


@app.get("/api/runs/{run_id}", response_model=RunOut)
def get_run(run_id: int, session: Session = Depends(get_session)) -> RunOut:
    run = session.get(Run, run_id)
    if not run:
        raise HTTPException(404, "run not found")
    return _run_to_out(run)
