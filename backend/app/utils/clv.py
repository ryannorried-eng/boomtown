from app.utils.odds_math import american_to_probability


def closing_line_value(entry_odds: int, closing_odds: int) -> float:
    implied_prob_taken = american_to_probability(entry_odds)
    implied_prob_close = american_to_probability(closing_odds)
    return (implied_prob_close - implied_prob_taken) * 10000
