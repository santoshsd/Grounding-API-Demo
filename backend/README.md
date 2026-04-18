# Grounding API Sample — Backend

FastAPI service that fans out a user query across multiple grounding-capable LLM APIs (and ungrounded baselines of each), then scores every response with an LLM-as-judge.

## Setup

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # fill in API keys
uvicorn app.main:app --reload --port 8000
```

## Key endpoints

- `POST /api/query` — run a query across selected providers, returns the full `Run` with `provider_calls` and `judge_scores`.
- `GET /api/runs` — list past runs.
- `GET /api/runs/{id}` — fetch one run with all details.

## Add a new provider

Drop a new file into `app/providers/` implementing the `Provider` protocol in `app/providers/base.py`, then register it in `app/config.py:PROVIDERS`.

## Tests

```bash
pytest
```
