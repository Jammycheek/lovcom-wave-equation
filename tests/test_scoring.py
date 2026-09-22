import math

from rcwe.scoring import score_predictions


def test_total_log_score_equals_per_row_sum():
    result = score_predictions([0.0, 0.25, 0.5, 0.75, 1.0], [0.1, 0.3, 0.5, 0.7, 0.9], 0.1)
    assert result.LS_total == math.fsum(row.log_probability for row in result.rows)
    assert result.LS_mean_per_IE == result.LS_total / 5
    assert len(result.rows) == 5
