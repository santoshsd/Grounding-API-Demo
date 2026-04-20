# Grounding API Sample

A side-by-side comparison tool for grounding-capable LLM APIs. Ask one question, fan it out across multiple providers with and without grounding, and see the delta in citations, latency, cost, and LLM-judged quality.

## Providers

| Provider | Grounded call | Baseline | Shown in UI |
|---|---|---|---|
| Gemini | `gemini-3-pro-preview` with `google_search` tool | same model, no tools | ✓ (unchecked by default) |
| Claude | `claude-sonnet-4-6` with `web_search_20250305` | same model, no tools | ✓ (checked by default) |
| OpenAI | `gpt-4o` via Responses API `web_search` tool | same model, no tools | ✓ (checked by default) |
| Tavily | Tavily Search API → Gemini synthesis | Gemini, no retrieval | ✓ (unchecked by default) |
| Exa | Exa Search API → Gemini synthesis | Gemini, no retrieval | ✓ (checked by default) |
| Perplexity | `sonar-pro` | `sonar` | hidden |
| Brave | Brave Search API → Gemini synthesis | Gemini, no retrieval | hidden |

### Hidden providers

Perplexity and Brave are fully implemented on the backend and still returned by `/api/providers`, but they are filtered out of the frontend UI. To re-enable them, edit `HIDDEN_PROVIDERS` in `frontend/components/QueryForm.tsx`. To change which providers are pre-checked when the page loads, edit `DEFAULT_SELECTED` in the same file.

## Quick start

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env            # fill in API keys you have
uvicorn app.main:app --reload --port 8000
```

You only need keys for the providers you want to compare; missing providers just return errors in their card.

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev                      # http://localhost:3000
```

## Usage

1. Open http://localhost:3000.
2. Paste a query where grounding matters — recent events, niche facts, verifiable claims.
3. Toggle providers on/off, keep "Include ungrounded baseline" on to see the delta.
4. Click **Run query**. Each provider card shows answer, citations, latency, cost, and a 1-5 judge score on correctness / groundedness / citation support.
5. Visit **Compare** for aggregate charts across all your past runs.

### Good test queries

- `Who won the 2025 Nobel Prize in Physics?` — freshness
- `Current CEO of [small private company]` — hallucination trap
- `Population of Lisbon in 2025` — verifiability with a citation

## Architecture

```
Next.js dashboard  ─▶  FastAPI backend  ─▶  7 provider adapters (async fan-out)
                                        └▶  LLM judge — Gemini or Claude (async fan-out)
                                        └▶  SQLite (runs, calls, scores)
```

Every provider adapter implements the same contract (`app/providers/base.py`) and returns a `ProviderResult`. Add a new one by dropping a file in `backend/app/providers/` and registering it in `app/config.py:PROVIDERS`.

## Tests

```bash
cd backend && pytest
```

## Layout

```
backend/
  app/
    main.py          # FastAPI routes
    config.py        # settings + provider registry
    db.py            # SQLModel tables
    schemas.py       # Pydantic contracts
    runner.py        # asyncio.gather fan-out
    judge.py         # Claude LLM-as-judge
    costs.py         # $/Mtok pricing table
    providers/       # one file per provider
  tests/
frontend/
  app/               # Next.js App Router
  components/        # QueryForm, ProviderCard, ResultsGrid, …
  lib/api.ts         # typed fetch wrappers
```
