"""Exa neural search (retrieval) + Gemini (synthesis)."""

import httpx

from ..config import get_settings
from ..schemas import ProviderResult
from . import _retrieval
from .base import stopwatch

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
    with stopwatch() as sw:
        if grounded:
            hits = await _search(query)
            answer, inp, out_tok, model = await _retrieval.synthesize(query, hits)
        else:
            hits = []
            answer, inp, out_tok, model = await _retrieval.ungrounded_gemini(query)
    return _retrieval.result(
        provider="exa",
        grounded=grounded,
        model=model,
        answer=answer,
        hits=hits,
        latency_ms=sw["ms"],
        inp=inp,
        out=out_tok,
    )
