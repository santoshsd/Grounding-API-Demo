import sys
import types

import pytest

from app.runner import fan_out
from app.schemas import Citation, ProviderResult


def _stub_provider(name: str):
    mod = types.ModuleType(f"app.providers.{name}")

    async def call(query: str, grounded: bool) -> ProviderResult:
        return ProviderResult(
            provider=name,
            grounded=grounded,
            model=f"{name}-model",
            answer=f"answer from {name} (grounded={grounded}) for {query}",
            citations=[Citation(url="https://example.com")] if grounded else [],
            latency_ms=10,
            input_tokens=100,
            output_tokens=50,
            cost_usd=0.001,
        )

    mod.call = call  # type: ignore[attr-defined]
    sys.modules[f"app.providers.{name}"] = mod


def _stub_failing(name: str):
    mod = types.ModuleType(f"app.providers.{name}")

    async def call(query: str, grounded: bool) -> ProviderResult:
        raise RuntimeError("boom")

    mod.call = call  # type: ignore[attr-defined]
    sys.modules[f"app.providers.{name}"] = mod


@pytest.mark.asyncio
async def test_fan_out_includes_grounded_and_ungrounded():
    _stub_provider("gemini")
    _stub_provider("claude")
    results = await fan_out("hello", ["gemini", "claude"], include_ungrounded=True)
    assert len(results) == 4
    grounded = [r for r in results if r.grounded]
    ungrounded = [r for r in results if not r.grounded]
    assert len(grounded) == 2 and len(ungrounded) == 2
    assert all(r.citations for r in grounded)
    assert all(not r.citations for r in ungrounded)


@pytest.mark.asyncio
async def test_fan_out_skips_ungrounded_when_disabled():
    _stub_provider("gemini")
    results = await fan_out("hello", ["gemini"], include_ungrounded=False)
    assert len(results) == 1
    assert results[0].grounded is True


@pytest.mark.asyncio
async def test_fan_out_isolates_failures():
    _stub_provider("gemini")
    _stub_failing("claude")
    results = await fan_out("hello", ["gemini", "claude"], include_ungrounded=False)
    assert len(results) == 2
    by_provider = {r.provider: r for r in results}
    assert by_provider["gemini"].error is None
    assert by_provider["claude"].error is not None and "boom" in by_provider["claude"].error


@pytest.mark.asyncio
async def test_fan_out_ignores_unknown_provider():
    results = await fan_out("hello", ["nonexistent"], include_ungrounded=True)
    assert results == []
