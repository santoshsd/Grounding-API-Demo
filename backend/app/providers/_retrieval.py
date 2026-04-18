"""Shared helpers for retrieval-only providers (Brave/Tavily/Exa).

Pattern: search API returns hits → feed hits to Gemini → return a grounded answer with citations.
"""

from google import genai

from ..config import get_settings
from ..costs import estimate_cost
from ..schemas import Citation, ProviderResult

SYSTEM = (
    "You are a careful research assistant. Answer the user's question using ONLY the "
    "provided SOURCES. Cite sources inline using [N] notation matching the numbered list. "
    "If the sources don't contain the answer, say so."
)


def build_prompt(query: str, hits: list[dict]) -> str:
    sources = "\n".join(
        f"[{i + 1}] {h.get('title', '')}\n{h.get('url', '')}\n{h.get('snippet', '')}"
        for i, h in enumerate(hits)
    )
    return f"{SYSTEM}\n\nSOURCES:\n{sources}\n\nQUESTION: {query}"


async def synthesize(query: str, hits: list[dict]) -> tuple[str, int | None, int | None, str]:
    """Run Gemini over the retrieved hits. Returns (answer, input_tokens, output_tokens, model)."""
    settings = get_settings()
    model = settings.retrieval_synthesis_model
    client = genai.Client(api_key=settings.google_api_key)
    prompt = build_prompt(query, hits)
    resp = await client.aio.models.generate_content(model=model, contents=prompt)
    usage = getattr(resp, "usage_metadata", None)
    inp = getattr(usage, "prompt_token_count", None) if usage else None
    out = getattr(usage, "candidates_token_count", None) if usage else None
    return (resp.text or ""), inp, out, model


def hits_to_citations(hits: list[dict]) -> list[Citation]:
    return [
        Citation(url=h["url"], title=h.get("title"), snippet=h.get("snippet"))
        for h in hits
        if h.get("url")
    ]


def result(
    provider: str,
    grounded: bool,
    model: str,
    answer: str,
    hits: list[dict],
    latency_ms: int,
    inp: int | None,
    out: int | None,
) -> ProviderResult:
    return ProviderResult(
        provider=provider,
        grounded=grounded,
        model=model,
        answer=answer,
        citations=hits_to_citations(hits) if grounded else [],
        latency_ms=latency_ms,
        input_tokens=inp,
        output_tokens=out,
        cost_usd=estimate_cost(provider, "google", model, inp, out, grounded),
        raw={"hit_count": len(hits)},
    )


async def ungrounded_gemini(query: str) -> tuple[str, int | None, int | None, str]:
    """Baseline: Gemini with no retrieval. Same synthesis model for an apples-to-apples baseline."""
    settings = get_settings()
    model = settings.retrieval_synthesis_model
    client = genai.Client(api_key=settings.google_api_key)
    resp = await client.aio.models.generate_content(model=model, contents=query)
    usage = getattr(resp, "usage_metadata", None)
    inp = getattr(usage, "prompt_token_count", None) if usage else None
    out = getattr(usage, "candidates_token_count", None) if usage else None
    return (resp.text or ""), inp, out, model
