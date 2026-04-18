import time
from contextlib import contextmanager
from typing import Iterator, Protocol

from ..schemas import ProviderResult


class Provider(Protocol):
    async def call(self, query: str, grounded: bool) -> ProviderResult: ...


@contextmanager
def stopwatch() -> Iterator[dict[str, int]]:
    start = time.perf_counter()
    box: dict[str, int] = {"ms": 0}
    try:
        yield box
    finally:
        box["ms"] = int((time.perf_counter() - start) * 1000)
