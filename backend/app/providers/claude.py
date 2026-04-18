from anthropic import AsyncAnthropic

from ..config import get_settings
from ..costs import estimate_cost
from ..schemas import Citation, ProviderResult
from .base import stopwatch

MODEL = "claude-sonnet-4-6"


async def call(query: str, grounded: bool) -> ProviderResult:
    settings = get_settings()
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    tools = (
        [{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}]
        if grounded
        else []
    )

    with stopwatch() as sw:
        resp = await client.messages.create(
            model=MODEL,
            max_tokens=2048,
            tools=tools,
            messages=[{"role": "user", "content": query}],
        )

    answer_parts: list[str] = []
    citations: list[Citation] = []
    for block in resp.content:
        if block.type == "text":
            answer_parts.append(block.text)
            for cit in getattr(block, "citations", []) or []:
                url = getattr(cit, "url", None)
                if url:
                    citations.append(
                        Citation(
                            url=url,
                            title=getattr(cit, "title", None),
                            snippet=getattr(cit, "cited_text", None),
                        )
                    )

    inp = resp.usage.input_tokens
    out = resp.usage.output_tokens

    return ProviderResult(
        provider="claude",
        grounded=grounded,
        model=MODEL,
        answer="".join(answer_parts),
        citations=citations,
        latency_ms=sw["ms"],
        input_tokens=inp,
        output_tokens=out,
        cost_usd=estimate_cost("claude", "anthropic", MODEL, inp, out, grounded),
        raw={"stop_reason": resp.stop_reason},
    )
