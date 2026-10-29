from app.checks.base import CheckIdentifier, EvidenceConfidence
from app.checks.speed import run_speed_check


def test_speed_check_skips_when_missing_or_negative():
    assert (
        run_speed_check(
            {"task_id": "t1", "worker_id": "w1", "answer": "Valid text", "seconds_spent": None}
        )
        is None
    )
    assert (
        run_speed_check(
            {"task_id": "t1", "worker_id": "w1", "answer": "Valid text", "seconds_spent": -5.0}
        )
        is None
    )
    assert (
        run_speed_check(
            {"task_id": "t1", "worker_id": "w1", "answer": "Valid text", "seconds_spent": 0}
        )
        is None
    )


def test_speed_check_flags_implausible_typing_velocity():
    long_answer = (
        "This is a detailed paragraph of 150 characters designed to test "
        "typing velocity bounds effectively in speed evaluation checks."
    )
    record = {
        "task_id": "t1",
        "worker_id": "w_fast",
        "answer": long_answer,
        "seconds_spent": 2.0,  # ~65 chars/sec, way above 15
    }
    finding = run_speed_check(record, threshold_chars_per_sec=15.0)
    assert finding is not None
    assert finding.check_identifier == CheckIdentifier.SPEED
    assert finding.evidence_confidence == EvidenceConfidence.LOW
    assert finding.numerical_measurements["characters_per_second"] > 50.0


def test_speed_check_passes_plausible_velocity():
    long_answer = "This is a normal paragraph typed at a realistic human typing pace."
    record = {
        "task_id": "t1",
        "worker_id": "w_normal",
        "answer": long_answer,
        "seconds_spent": 25.0,  # ~2.6 chars/sec
    }
    finding = run_speed_check(record, threshold_chars_per_sec=15.0)
    assert finding is None
