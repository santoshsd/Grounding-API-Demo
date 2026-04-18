import asyncio
import importlib
from typing import Callable, Awaitable

from .config import PROVIDERS, get_settings
from .schemas import ProviderResult


ProviderFn = Callable[[str, bool], Awaitable[ProviderResult]]


def _load(name: str) -> ProviderFn:
    mod = importlib.import_module(f"app.providers.{name}")
    return mod.call


async def _guarded(fn: ProviderFn, name: str, query: str, grounded: bool) -> ProviderResult:
    timeout = get_settings().request_timeout_s
    try:
        return await asyncio.wait_for(fn(query, grounded), timeout=timeout)
    except asyncio.TimeoutError:
        return ProviderResult(
            provider=name,
            grounded=grounded,
            model="",
            answer="",
            latency_ms=timeout * 1000,
            error=f"timeout after {timeout}s",
        )
    except Exception as exc:  # noqa: BLE001
        return ProviderResult(
            provider=name,
            grounded=grounded,
            model="",
            answer="",
            latency_ms=0,
            error=f"{type(exc).__name__}: {exc}",
        )


async def fan_out(
    query: str, providers: list[str], include_ungrounded: bool
) -> list[ProviderResult]:
    selected = [p for p in providers if p in PROVIDERS]
    tasks: list[asyncio.Task[ProviderResult]] = []
    for name in selected:
        fn = _load(name)
        tasks.append(asyncio.create_task(_guarded(fn, name, query, True)))
        if include_ungrounded:
            tasks.append(asyncio.create_task(_guarded(fn, name, query, False)))
    return await asyncio.gather(*tasks)
