from app.costs import estimate_cost


def test_known_model_cost():
    cost = estimate_cost("openai_ws", "openai", "gpt-4o", 1000, 500, grounded=False)
    assert cost == round((1000 * 2.50 + 500 * 10.00) / 1_000_000, 6)


def test_grounding_surcharge_added():
    base = estimate_cost("openai_ws", "openai", "gpt-4o", 1000, 500, grounded=False)
    surcharged = estimate_cost("openai_ws", "openai", "gpt-4o", 1000, 500, grounded=True)
    assert surcharged is not None and base is not None
    assert surcharged > base


def test_unknown_model_returns_none():
    assert estimate_cost("x", "x", "unknown-model", 10, 10, grounded=False) is None


def test_missing_tokens_returns_none():
    assert estimate_cost("openai_ws", "openai", "gpt-4o", None, None, grounded=False) is None
