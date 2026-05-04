"""Exa neural search (retrieval) + Gemini (synthesis)."""

import time

import httpx

from ..config import get_settings
from ..schemas import ProviderResult, TimingStage
from . import _retrieval

ENDPOINT = "https://api.exa.ai/search"
TOP_K = 6


async def _search(query: str) -> list[dict]:
    settings = get_settings()
    async with httpx.AsyncClient(timeout=settings.request_timeout_s) as client:
        r = await client.post(
            ENDPOINT,
            headers={
                "x-api-key": settings.exa_api_key or "",
                "Content-Type": "application/json",
            },
            json={
                "query": query,
                "numResults": TOP_K,
                "contents": {"text": {"maxCharacters": 1000}},
            },
        )
        r.raise_for_status()
        data = r.json()
    out = []
    for h in data.get("results", []):
        text = h.get("text") or ""
        out.append(
            {
                "title": h.get("title"),
                "url": h.get("url"),
                "snippet": text[:500],
            }
        )
    return out


async def call(query: str, grounded: bool) -> ProviderResult:
    timings: list[TimingStage] = []
    t_run = time.perf_counter()
    if grounded:
        t0 = time.perf_counter()
        hits = await _search(query)
        timings.append(
            TimingStage(stage="exa_search", ms=int((time.perf_counter() - t0) * 1000))
        )
        t1 = time.perf_counter()
        answer, inp, out_tok, model = await _retrieval.synthesize(query, hits)
        timings.append(
            TimingStage(stage="gemini_synthesis", ms=int((time.perf_counter() - t1) * 1000))
        )
    else:
        hits = []
        t0 = time.perf_counter()
        answer, inp, out_tok, model = await _retrieval.ungrounded_gemini(query)
        timings.append(
            TimingStage(stage="gemini_baseline", ms=int((time.perf_counter() - t0) * 1000))
        )
    total_ms = int((time.perf_counter() - t_run) * 1000)
    return _retrieval.result(
        provider="exa",
        grounded=grounded,
        model=model,
        answer=answer,
        hits=hits,
        latency_ms=total_ms,
        inp=inp,
        out=out_tok,
        timings=timings,
    )
