from openai import AsyncOpenAI

from ..config import get_settings
from ..costs import estimate_cost
from ..schemas import Citation, ProviderResult, TimingStage
from .base import stopwatch

MODEL = "gpt-4o"


async def call(query: str, grounded: bool) -> ProviderResult:
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    kwargs: dict = {"model": MODEL, "input": query}
    if grounded:
        kwargs["tools"] = [{"type": "web_search"}]

    with stopwatch() as sw:
        resp = await client.responses.create(**kwargs)

    answer = getattr(resp, "output_text", "") or ""
    citations: list[Citation] = []

    for item in getattr(resp, "output", []) or []:
        content = getattr(item, "content", None) or []
        for block in content:
            for ann in getattr(block, "annotations", []) or []:
                if getattr(ann, "type", None) == "url_citation":
                    citations.append(
                        Citation(
                            url=getattr(ann, "url", ""),
                            title=getattr(ann, "title", None),
                        )
                    )

    usage = getattr(resp, "usage", None)
    inp = getattr(usage, "input_tokens", None) if usage else None
    out = getattr(usage, "output_tokens", None) if usage else None

    return ProviderResult(
        provider="openai_ws",
        grounded=grounded,
        model=MODEL,
        answer=answer,
        citations=citations,
        latency_ms=sw["ms"],
        input_tokens=inp,
        output_tokens=out,
        cost_usd=estimate_cost("openai_ws", "openai", MODEL, inp, out, grounded),
        raw={"id": getattr(resp, "id", None)},
        timings=[TimingStage(stage="responses.create", ms=sw["ms"])],
    )
