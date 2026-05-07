"""Smoke tests for retrieval providers (Brave, Tavily, Exa).

We mock:
  - httpx calls (respx) to the search API
  - the shared `_retrieval.synthesize` + `ungrounded_gemini` functions (monkeypatch) so
    we never hit Gemini.

Goal: confirm each provider maps its API response into the common ProviderResult shape.
"""

import httpx
import pytest
import respx

from app.providers import _retrieval, brave, exa, parallel, tavily


@pytest.fixture(autouse=True)
def _fake_gemini(monkeypatch):
    async def fake_synthesize(query, hits):
        return (f"Synthesized answer about {query} using {len(hits)} sources.", 100, 50, "gemini-2.5-flash")

    async def fake_ungrounded(query):
        return (f"Baseline answer about {query}.", 80, 40, "gemini-2.5-flash")

    monkeypatch.setattr(_retrieval, "synthesize", fake_synthesize)
    monkeypatch.setattr(_retrieval, "ungrounded_gemini", fake_ungrounded)


@pytest.fixture(autouse=True)
def _fake_keys(monkeypatch):
    from app import config

    config.get_settings.cache_clear()
    monkeypatch.setenv("GOOGLE_API_KEY", "test")
    monkeypatch.setenv("BRAVE_API_KEY", "test")
    monkeypatch.setenv("TAVILY_API_KEY", "test")
    monkeypatch.setenv("EXA_API_KEY", "test")
    monkeypatch.setenv("PARALLEL_API_KEY", "test")
    yield
    config.get_settings.cache_clear()


@pytest.mark.asyncio
@respx.mock
async def test_brave_grounded_maps_results():
    respx.get("https://api.search.brave.com/res/v1/web/search").mock(
        return_value=httpx.Response(
            200,
            json={
                "web": {
                    "results": [
                        {"title": "T1", "url": "https://a.com", "description": "d1"},
                        {"title": "T2", "url": "https://b.com", "description": "d2"},
                    ]
                }
            },
        )
    )
    r = await brave.call("what is x?", grounded=True)
    assert r.provider == "brave" and r.grounded
    assert r.error is None
    assert len(r.citations) == 2
    assert r.citations[0].url == "https://a.com"
    assert "Synthesized answer" in r.answer


@pytest.mark.asyncio
async def test_brave_ungrounded_skips_search():
    r = await brave.call("what is x?", grounded=False)
    assert r.grounded is False
    assert r.citations == []
    assert "Baseline answer" in r.answer


@pytest.mark.asyncio
@respx.mock
async def test_tavily_grounded_maps_results():
    respx.post("https://api.tavily.com/search").mock(
        return_value=httpx.Response(
            200,
            json={
                "results": [
                    {"title": "T1", "url": "https://a.com", "content": "c1"},
                    {"title": "T2", "url": "https://b.com", "content": "c2"},
                    {"title": "T3", "url": "https://c.com", "content": "c3"},
                ]
            },
        )
    )
    r = await tavily.call("what is x?", grounded=True)
    assert r.provider == "tavily" and r.grounded
    assert len(r.citations) == 3
    assert {c.url for c in r.citations} == {"https://a.com", "https://b.com", "https://c.com"}


@pytest.mark.asyncio
async def test_tavily_ungrounded_skips_search():
    r = await tavily.call("what is x?", grounded=False)
    assert r.grounded is False
    assert r.citations == []


@pytest.mark.asyncio
@respx.mock
async def test_exa_grounded_maps_results():
    respx.post("https://api.exa.ai/search").mock(
        return_value=httpx.Response(
            200,
            json={
                "results": [
                    {"title": "T1", "url": "https://a.com", "text": "long text 1"},
                    {"title": "T2", "url": "https://b.com", "text": "long text 2"},
                ]
            },
        )
    )
    r = await exa.call("what is x?", grounded=True)
    assert r.provider == "exa" and r.grounded
    assert len(r.citations) == 2
    assert r.citations[0].snippet == "long text 1"


@pytest.mark.asyncio
async def test_exa_ungrounded_skips_search():
    r = await exa.call("what is x?", grounded=False)
    assert r.grounded is False
    assert r.citations == []


@pytest.mark.asyncio
@respx.mock
async def test_parallel_grounded_maps_results():
    respx.post("https://api.parallel.ai/v1/search").mock(
        return_value=httpx.Response(
            200,
            json={
                "search_id": "s1",
                "results": [
                    {
                        "url": "https://a.com",
                        "title": "T1",
                        "excerpts": ["excerpt one"],
                    },
                    {
                        "url": "https://b.com",
                        "title": "T2",
                        "excerpts": ["excerpt two"],
                    },
                ],
                "session_id": "sess",
            },
        )
    )
    r = await parallel.call("what is quantum computing?", grounded=True)
    assert r.provider == "parallel" and r.grounded
    assert len(r.citations) == 2
    assert r.citations[0].url == "https://a.com"
    assert "Synthesized answer" in r.answer


@pytest.mark.asyncio
async def test_parallel_ungrounded_skips_search():
    r = await parallel.call("what is x?", grounded=False)
    assert r.grounded is False
    assert r.citations == []


@pytest.mark.asyncio
@respx.mock
async def test_brave_propagates_http_error():
    respx.get("https://api.search.brave.com/res/v1/web/search").mock(
        return_value=httpx.Response(401, json={"error": "unauthorized"})
    )
    with pytest.raises(httpx.HTTPStatusError):
        await brave.call("what is x?", grounded=True)
