"""Single-line JSON logs for Railway Log Explorer.

Each completed POST /api/query emits one stdout line. In Railway Observability, filter by
the substring ``query_complete`` or JSON field ``message`` / ``run_id``.

Environment: ``LOG_QUERY_PREVIEW_CHARS`` — if > 0, adds truncated ``query_preview`` (default 0 omits query text).
"""

import json
import logging
import sys
from typing import Any

from .config import get_settings
from .schemas import ProviderResult

# Message-only formatter so each line is valid JSON (no `INFO:logger:` prefix).
_logger = logging.getLogger("app.query_complete")
if not _logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter("%(message)s"))
    _logger.addHandler(_handler)
    _logger.propagate = False
    _logger.setLevel(logging.INFO)


def log_query_complete(
    *,
    run_id: int,
    fan_out_ms: int,
    judge_ms: int | None,
    run_judge: bool,
    results: list[ProviderResult],
    query_text: str,
) -> None:
    settings = get_settings()
    max_chars = settings.log_query_preview_chars

    calls: list[dict[str, Any]] = []
    for r in results:
        calls.append(
            {
                "provider": r.provider,
                "grounded": r.grounded,
                "latency_ms": r.latency_ms,
                "error": bool(r.error),
                "timings": [t.model_dump() for t in r.timings],
            }
        )

    payload: dict[str, Any] = {
        "level": "warn" if results and all(r.error for r in results) else "info",
        "message": "query_complete",
        "run_id": run_id,
        "fan_out_ms": fan_out_ms,
        "judge_ms": judge_ms if run_judge else None,
        "provider_count": len(results),
        "calls": calls,
    }

    if max_chars > 0:
        q = query_text.strip()
        payload["query_preview"] = (
            q[:max_chars] + ("…" if len(q) > max_chars else "")
        )

    line = json.dumps(payload, default=str)
    _logger.info("%s", line)
