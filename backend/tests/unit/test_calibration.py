from app.services.calibration import (
    calculate_sample_calibration,
    wilson_score_interval,
)


def test_wilson_score_interval_bounds():
    # 0 positive out of 50 samples
    lower, upper = wilson_score_interval(0, 50)
    assert lower == 0.0
    assert 0.05 < upper < 0.10  # Upper bound non-zero reflecting uncertainty

    # 5 positive out of 100 samples (5%)
    lower, upper = wilson_score_interval(5, 100)
    assert 0.01 < lower < 0.05
    assert 0.05 < upper < 0.12

    # Perfect detection 50 out of 50 (100%)
    lower, upper = wilson_score_interval(50, 50)
    assert 0.90 < lower < 1.0
    assert upper == 1.0


def test_sample_calibration_insufficient_sample_guard():
    # n=15 < 30 minimum threshold (FR-43)
    res = calculate_sample_calibration(sample_size=15, flagged_count=1, min_sample_size=30)
    assert res["insufficient_data_reason"] is not None
    assert "Sample size below recommended calibration threshold" in res["insufficient_data_reason"]
    assert res["estimated_fp_rate"] == round(1 / 15, 4)

    # n=50 >= 30 threshold
    res_sufficient = calculate_sample_calibration(
        sample_size=50, flagged_count=1, min_sample_size=30
    )
    assert res_sufficient["insufficient_data_reason"] is None
