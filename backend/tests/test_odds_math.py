import pytest

from app.utils.odds_math import (
    american_to_decimal,
    american_to_probability,
    decimal_to_american,
    probability_to_american,
)


def test_american_decimal_roundtrip_known_values():
    assert american_to_decimal(150) == pytest.approx(2.5)
    assert american_to_decimal(-200) == pytest.approx(1.5)
    assert decimal_to_american(2.5) == 150
    assert decimal_to_american(1.5) == -200


def test_implied_probability_known_values():
    assert american_to_probability(100) == pytest.approx(0.5)
    assert american_to_probability(-150) == pytest.approx(0.6)
    assert probability_to_american(0.5) == -100
    assert probability_to_american(0.4) == 150
