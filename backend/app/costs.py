"""Rough per-million-token pricing. Update as providers change rates.

Values are USD per 1M tokens: (input, output).
"""

PRICING: dict[tuple[str, str], tuple[float, float]] = {
    ("openai", "gpt-4o"): (2.50, 10.00),
    ("openai", "gpt-4o-mini"): (0.15, 0.60),
    ("anthropic", "claude-sonnet-4-6"): (3.00, 15.00),
    ("anthropic", "claude-opus-4-7"): (15.00, 75.00),
    ("google", "gemini-2.5-pro"): (1.25, 10.00),
    ("google", "gemini-2.5-flash"): (0.30, 2.50),
    ("perplexity", "sonar-pro"): (3.00, 15.00),
    ("perplexity", "sonar"): (1.00, 1.00),
}

# Flat per-request surcharges for grounding/search tools, USD.
GROUNDING_SURCHARGE: dict[str, float] = {
    "openai_ws": 0.025,
    "claude": 0.010,
    "gemini": 0.000,
    "perplexity": 0.000,
    "brave": 0.000,
    "tavily": 0.000,
    "exa": 0.005,
    "parallel": 0.000,
}


def estimate_cost(
    provider_key: str,
    vendor: str,
    model: str,
    input_tokens: int | None,
    output_tokens: int | None,
    grounded: bool,
) -> float | None:
    price = PRICING.get((vendor, model))
    if price is None or input_tokens is None or output_tokens is None:
        return None
    inp, out = price
    total = (input_tokens * inp + output_tokens * out) / 1_000_000
    if grounded:
        total += GROUNDING_SURCHARGE.get(provider_key, 0.0)
    return round(total, 6)
