"""Brave Search (retrieval) + Gemini (synthesis)."""

import httpx

from ..config import get_settings
from ..schemas import ProviderResult
from . import _retrieval
from .base import stopwatch

ENDPOINT = "https://api.search.brave.com/res/v1/web/search"
TOP_K = 6


async def _search(query: str) -> list[dict]:
    settings = get_settings()
    async with httpx.AsyncClient(timeout=settings.request_timeout_s) as client:
        r = await client.get(
            ENDPOINT,
            headers={
                "X-Subscription-Token": settings.brave_api_key or "",
                "Accept": "application/json",
            },
            params={"q": query, "count": TOP_K},
        )
        r.raise_for_status()
        data = r.json()
    results = (data.get("web") or {}).get("results") or []
    return [
        {
            "title": r.get("title"),
            "url": r.get("url"),
            "snippet": r.get("description"),
        }
        for r in results
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
        provider="brave",
        grounded=grounded,
        model=model,
        answer=answer,
        hits=hits,
        latency_ms=sw["ms"],
        inp=inp,
        out=out,
    )
