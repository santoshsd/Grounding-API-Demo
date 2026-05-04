import json
from unittest.mock import patch

from app.query_log import log_query_complete
from app.schemas import Citation, ProviderResult, TimingStage


def test_log_query_complete_emits_valid_json_with_expected_keys(capsys):
    results = [
        ProviderResult(
            provider="gemini",
            grounded=True,
            model="m",
            answer="a",
            citations=[Citation(url="https://x.com")],
            latency_ms=100,
            timings=[TimingStage(stage="generate_content", ms=100)],
        ),
        ProviderResult(
            provider="claude",
            grounded=False,
            model="m2",
            answer="",
            latency_ms=50,
            error="boom",
            timings=[],
        ),
    ]
    with patch("app.query_log.get_settings") as gs:
        gs.return_value.log_query_preview_chars = 0
        log_query_complete(
            run_id=42,
            fan_out_ms=500,
            judge_ms=1200,
            run_judge=True,
            results=results,
            query_text="secret",
        )
    out = capsys.readouterr().out.strip()
    data = json.loads(out)
    assert data["message"] == "query_complete"
    assert data["run_id"] == 42
    assert data["fan_out_ms"] == 500
    assert data["judge_ms"] == 1200
    assert data["provider_count"] == 2
    assert data["level"] == "info"
    assert len(data["calls"]) == 2
    assert data["calls"][0]["provider"] == "gemini"
    assert data["calls"][0]["error"] is False
    assert data["calls"][0]["timings"][0]["stage"] == "generate_content"
    assert data["calls"][1]["error"] is True
    assert "query_preview" not in data


def test_log_query_preview_when_chars_set(capsys):
    with patch("app.query_log.get_settings") as gs:
        gs.return_value.log_query_preview_chars = 4
        log_query_complete(
            run_id=1,
            fan_out_ms=1,
            judge_ms=None,
            run_judge=False,
            results=[],
            query_text="hello world",
        )
    data = json.loads(capsys.readouterr().out.strip())
    assert data["query_preview"] == "hell…"
    assert data["judge_ms"] is None
