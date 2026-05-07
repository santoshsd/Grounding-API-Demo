"""Parallel Search API (retrieval) + Gemini (synthesis).

Uses Parallel Web Search: https://docs.parallel.ai/search/search-quickstart
"""

import time

import httpx

from ..config import get_settings
from ..schemas import ProviderResult, TimingStage
from . import _retrieval

ENDPOINT = "https://api.parallel.ai/v1/search"
TOP_K = 6


def _keyword_queries(user_query: str) -> list[str]:
    """Parallel expects 2–3 short keyword queries alongside the objective."""
    words = user_query.strip().split()
    if not words:
        return ["fact lookup", "current information"]
    q1 = " ".join(words[:6])
    rest = words[6:12]
    q2 = " ".join(rest) if rest else ""
    if not q2 or q2 == q1:
        q2 = " ".join(words[: min(3, len(words))]) + " details"
    if q2.strip() == q1.strip():
        q2 = q1 + " latest"
    return [q1, q2]


async def _search(query: str) -> list[dict]:
    settings = get_settings()

    payload: dict = {
        "objective": query,
        "search_queries": _keyword_queries(query),
        "mode": "advanced",
    }

    async with httpx.AsyncClient(timeout=settings.request_timeout_s) as client:
        r = await client.post(
            ENDPOINT,
            headers={
                "x-api-key": settings.parallel_api_key or "",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        r.raise_for_status()
        data = r.json()

    out: list[dict] = []
    for h in (data.get("results") or [])[:TOP_K]:
        url = h.get("url")
        if not url:
            continue
        excerpts = h.get("excerpts") or []
        text = "\n\n".join(str(x) for x in excerpts if x)
        out.append(
            {
                "title": h.get("title"),
                "url": url,
                "snippet": text[:3000] if text else None,
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
            TimingStage(stage="parallel_search", ms=int((time.perf_counter() - t0) * 1000))
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
        provider="parallel",
        grounded=grounded,
        model=model,
        answer=answer,
        hits=hits,
        latency_ms=total_ms,
        inp=inp,
        out=out_tok,
        timings=timings,
    )
