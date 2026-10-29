import math
from typing import Any, Dict, Optional, Tuple

DEFAULT_CONFIDENCE_LEVEL = 0.95
DEFAULT_MIN_SAMPLE_SIZE = 30


def wilson_score_interval(
    successes: int,
    total: int,
    confidence: float = DEFAULT_CONFIDENCE_LEVEL,
) -> Tuple[float, float]:
    """
    Computes Wilson score confidence interval for a binomial proportion (FR-43).
    Ensures asymmetric, mathematically valid bounds even near 0 or 1.
    """
    if total <= 0:
        return 0.0, 1.0

    # For 95% confidence, z ~ 1.95996
    z_values = {
        0.90: 1.64485,
        0.95: 1.95996,
        0.99: 2.57583,
    }
    z = z_values.get(confidence, 1.95996)

    p_hat = float(successes) / float(total)
    n = float(total)

    denominator = 1.0 + (z**2 / n)
    center = (p_hat + (z**2 / (2.0 * n))) / denominator

    spread = (z / denominator) * math.sqrt((p_hat * (1.0 - p_hat) / n) + (z**2 / (4.0 * n**2)))

    lower = max(0.0, center - spread)
    upper = min(1.0, center + spread)

    return round(lower, 4), round(upper, 4)


def calculate_sample_calibration(
    sample_size: int,
    flagged_count: int,
    min_sample_size: int = DEFAULT_MIN_SAMPLE_SIZE,
) -> Dict[str, Any]:
    """
    Evaluates human-labeled baseline calibration and Wilson confidence interval.
    Flags insufficient data reason if sample size is below threshold (FR-43).
    """
    if sample_size <= 0:
        return {
            "sample_size": 0,
            "flagged_count": 0,
            "estimated_fp_rate": 0.0,
            "ci_lower": 0.0,
            "ci_upper": 1.0,
            "ci_method": "wilson",
            "insufficient_data_reason": "No baseline sample provided.",
        }

    fp_rate = round(float(flagged_count) / float(sample_size), 4)
    ci_lower, ci_upper = wilson_score_interval(flagged_count, sample_size)

    insufficient_reason: Optional[str] = None
    if sample_size < min_sample_size:
        insufficient_reason = (
            f"Sample size below recommended calibration threshold "
            f"(n={sample_size} < {min_sample_size}); uncertainty bounds may be broad."
        )

    return {
        "sample_size": sample_size,
        "flagged_count": flagged_count,
        "estimated_fp_rate": fp_rate,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "ci_method": "wilson",
        "insufficient_data_reason": insufficient_reason,
    }
