import httpx

from ..config import get_settings
from ..costs import estimate_cost
from ..schemas import Citation, ProviderResult
from .base import stopwatch

ENDPOINT = "https://api.perplexity.ai/chat/completions"
GROUNDED_MODEL = "sonar-pro"
UNGROUNDED_MODEL = "sonar"


async def call(query: str, grounded: bool) -> ProviderResult:
    settings = get_settings()
    model = GROUNDED_MODEL if grounded else UNGROUNDED_MODEL

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": query}],
    }

    async with httpx.AsyncClient(timeout=settings.request_timeout_s) as client:
        with stopwatch() as sw:
            r = await client.post(
                ENDPOINT,
                headers={
                    "Authorization": f"Bearer {settings.perplexity_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            r.raise_for_status()
            data = r.json()

    choice = data["choices"][0]["message"]
    answer = choice.get("content", "")

    citations: list[Citation] = []
    for url in data.get("citations", []) or []:
        citations.append(Citation(url=url))
    for c in choice.get("citations", []) or []:
        if isinstance(c, dict) and c.get("url"):
            citations.append(Citation(url=c["url"], title=c.get("title")))

    usage = data.get("usage", {})
    inp = usage.get("prompt_tokens")
    out = usage.get("completion_tokens")

    return ProviderResult(
        provider="perplexity",
        grounded=grounded,
        model=model,
        answer=answer,
        citations=citations,
        latency_ms=sw["ms"],
        input_tokens=inp,
        output_tokens=out,
        cost_usd=estimate_cost("perplexity", "perplexity", model, inp, out, grounded),
        raw={"id": data.get("id")},
    )
