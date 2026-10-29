from typing import Any, Dict, Optional

from app.checks.base import CheckFinding, CheckIdentifier, EvidenceConfidence

DEFAULT_TYPING_VELOCITY_THRESHOLD = 15.0  # characters per second


def run_speed_check(
    answer_record: Dict[str, Any],
    threshold_chars_per_sec: float = DEFAULT_TYPING_VELOCITY_THRESHOLD,
) -> Optional[CheckFinding]:
    """
    Evaluates typing plausibility based on character velocity when timing metadata is present.
    Requirements FR-27 and FR-28.
    """
    seconds_spent = answer_record.get("seconds_spent")
    answer_text = answer_record.get("answer", "")

    # FR-28: Gracefully skip when timing data is absent or non-positive
    if seconds_spent is None or seconds_spent <= 0 or not answer_text:
        return None

    answer_len = len(answer_text.strip())
    if answer_len < 30:  # Ignore trivial brief responses
        return None

    velocity = answer_len / float(seconds_spent)

    if velocity > threshold_chars_per_sec:
        return CheckFinding(
            task_id=answer_record["task_id"],
            worker_id=answer_record["worker_id"],
            check_identifier=CheckIdentifier.SPEED,
            finding_type="implausible_typing_velocity",
            evidence_confidence=EvidenceConfidence.LOW,
            explanation=(
                f"Answer was submitted with a typing velocity of {velocity:.1f} chars/sec "
                f"({answer_len} characters in {seconds_spent:.1f} seconds), exceeding "
                f"plausibility threshold of {threshold_chars_per_sec:.1f} chars/sec (~180 WPM)."
            ),
            evidence_text=answer_text[:120] + ("..." if answer_len > 120 else ""),
            numerical_measurements={
                "characters_per_second": round(velocity, 2),
                "seconds_spent": round(float(seconds_spent), 1),
                "answer_length_chars": answer_len,
                "threshold_chars_per_sec": threshold_chars_per_sec,
            },
            limitations=(
                "Speed analysis is an auxiliary indicator (Low confidence). Fast submission could "
                "indicate pre-written notes, fast copy-pasting, or inaccurate timer logging."
            ),
        )

    return None
