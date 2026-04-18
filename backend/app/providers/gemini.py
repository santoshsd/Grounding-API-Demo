from google import genai
from google.genai import types

from ..config import get_settings
from ..costs import estimate_cost
from ..schemas import Citation, ProviderResult
from .base import stopwatch

MODEL = "gemini-2.5-pro"


async def call(query: str, grounded: bool) -> ProviderResult:
    settings = get_settings()
    client = genai.Client(api_key=settings.google_api_key)

    config = types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())] if grounded else None
    )

    with stopwatch() as sw:
        resp = await client.aio.models.generate_content(
            model=MODEL, contents=query, config=config
        )

    answer = resp.text or ""
    citations: list[Citation] = []
    if grounded:
        meta = getattr(resp.candidates[0], "grounding_metadata", None) if resp.candidates else None
        chunks = getattr(meta, "grounding_chunks", None) or [] if meta else []
        for ch in chunks:
            web = getattr(ch, "web", None)
            if web and getattr(web, "uri", None):
                citations.append(Citation(url=web.uri, title=getattr(web, "title", None)))

    usage = getattr(resp, "usage_metadata", None)
    inp = getattr(usage, "prompt_token_count", None) if usage else None
    out = getattr(usage, "candidates_token_count", None) if usage else None

    return ProviderResult(
        provider="gemini",
        grounded=grounded,
        model=MODEL,
        answer=answer,
        citations=citations,
        latency_ms=sw["ms"],
        input_tokens=inp,
        output_tokens=out,
        cost_usd=estimate_cost("gemini", "google", MODEL, inp, out, grounded),
        raw={"text": answer},
    )
