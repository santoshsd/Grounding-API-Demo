"""Tavily Search (retrieval) + Gemini (synthesis)."""

import httpx

from ..config import get_settings
from ..schemas import ProviderResult
from . import _retrieval
from .base import stopwatch

ENDPOINT = "https://api.tavily.com/search"
TOP_K = 6


async def _search(query: str) -> list[dict]:
    settings = get_settings()
    async with httpx.AsyncClient(timeout=settings.request_timeout_s) as client:
        r = await client.post(
            ENDPOINT,
            json={
                "api_key": settings.tavily_api_key,
                "query": query,
                "max_results": TOP_K,
                "search_depth": "advanced",
            },
        )
        r.raise_for_status()
        data = r.json()
    return [
        {
            "title": h.get("title"),
            "url": h.get("url"),
            "snippet": h.get("content"),
        }
        for h in data.get("results", [])
    ]


async def call(query: str, grounded: bool) -> ProviderResult:
    with stopwatch() as sw:
        if grounded:
            hits = await _search(query)
            answer, inp, out, model = await _retrieval.synthesize(query, hits)
        else:
            hits = []
            answer, inp, out, model = await _retrieval.ungrounded_gemini(query)
    return _retrieval.result(
        provider="tavily",
        grounded=grounded,
        model=model,
        answer=answer,
        hits=hits,
        latency_ms=sw["ms"],
        inp=inp,
        out=out,
    )
