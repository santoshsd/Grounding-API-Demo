import json
import re

from anthropic import AsyncAnthropic
from google import genai
from google.genai import types

from .config import get_settings
from .schemas import JudgeScore, ProviderResult

JUDGE_PROMPT = """You are evaluating an LLM response to a user query. Score each dimension \
on an integer scale from 1 (poor) to 5 (excellent):

- correctness: Is the factual content accurate based on what you know? Penalize hallucinations.
- groundedness: Does the answer appear anchored in the cited sources vs. invented or speculative?
- citation_support: Do the citations (if any) actually support the claims? If no citations are \
  provided, score 1 unless the answer is a refusal or admission of ignorance (then score 3).

Respond in strict JSON: {{"correctness": N, "groundedness": N, "citation_support": N, \
"rationale": "one short sentence"}}.

USER QUERY:
{query}

MODEL ANSWER:
{answer}

CITATIONS:
{citations}
"""


def _extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in judge output: {text[:200]}")
    return json.loads(match.group(0))


def _build_prompt(query: str, result: ProviderResult) -> str:
    citations_text = (
        "\n".join(f"- {c.url} — {c.title or ''}" for c in result.citations) or "(none)"
    )
    return JUDGE_PROMPT.format(
        query=query, answer=result.answer, citations=citations_text
    )


async def _score_anthropic(prompt: str) -> str:
    settings = get_settings()
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    resp = await client.messages.create(
        model=settings.judge_model_anthropic,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in resp.content if b.type == "text")


async def _score_google(prompt: str) -> str:
    """Gemini judge with Google Search grounding.

    Two-step: first call uses google_search so the judge can verify current facts; a
    second call (no tools, JSON mode) distills the verification into strict JSON.
    Can't combine tools + response_mime_type=json in one call.
    """
    settings = get_settings()
    client = genai.Client(api_key=settings.google_api_key)

    verify_prompt = (
        prompt
        + "\n\nBefore scoring, use Google Search to verify any time-sensitive facts "
        "(recent events, people, prices). Then produce the scores."
    )
    grounded = await client.aio.models.generate_content(
        model=settings.judge_model_google,
        contents=verify_prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
        ),
    )
    reasoning = grounded.text or ""

    distill = await client.aio.models.generate_content(
        model=settings.judge_model_google,
        contents=(
            "Given the following judge reasoning, extract the final scores as strict JSON "
            'in the shape {"correctness": N, "groundedness": N, "citation_support": N, '
            '"rationale": "one short sentence"}. Do not include any other text.\n\n'
            f"REASONING:\n{reasoning}"
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    return distill.text or ""


def _judge_available(provider: str | None) -> str | None:
    """Return the effective judge provider, or None if no keys are configured."""
    settings = get_settings()
    candidate = (provider or settings.judge_provider or "google").lower()
    if candidate == "google" and settings.google_api_key:
        return "google"
    if candidate == "anthropic" and settings.anthropic_api_key:
        return "anthropic"
    # fall back to whichever key exists
    if settings.google_api_key:
        return "google"
    if settings.anthropic_api_key:
        return "anthropic"
    return None


async def score(
    query: str, result: ProviderResult, judge_provider: str | None = None
) -> JudgeScore | None:
    if result.error:
        return None
    effective = _judge_available(judge_provider)
    if effective is None:
        return None

    prompt = _build_prompt(query, result)
    settings = get_settings()
    judge_model = (
        settings.judge_model_anthropic
        if effective == "anthropic"
        else settings.judge_model_google
    )
    try:
        text = (
            await _score_anthropic(prompt)
            if effective == "anthropic"
            else await _score_google(prompt)
        )
        data = _extract_json(text)
        return JudgeScore(
            correctness=int(data["correctness"]),
            groundedness=int(data["groundedness"]),
            citation_support=int(data["citation_support"]),
            rationale=str(data.get("rationale", "")),
            judge_provider=effective,
            judge_model=judge_model,
        )
    except (ValueError, KeyError, json.JSONDecodeError, Exception):  # noqa: BLE001
        return None
