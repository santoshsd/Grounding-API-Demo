# Grounding API Sample

A side-by-side comparison tool for grounding-capable LLM APIs. Ask one question, fan it out across multiple providers with and without grounding, and see the delta in citations, latency, cost, and LLM-judged quality.

## Providers

| Provider | Grounded call | Baseline |
|---|---|---|
| Bing + GPT-4o | Bing Web Search v7 retrieval → GPT-4o synthesis | GPT-4o only |
| Gemini | `gemini-2.5-pro` with `google_search` tool | same model, no tools |
| Claude | `claude-sonnet-4-6` with `web_search_20250305` | same model, no tools |
| OpenAI | `gpt-4o` via Responses API `web_search` tool | same model, no tools |
| Perplexity | `sonar-pro` | `sonar` |

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
Next.js dashboard  ─▶  FastAPI backend  ─▶  5 provider adapters (async fan-out)
                                        └▶  Claude judge (async fan-out)
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
