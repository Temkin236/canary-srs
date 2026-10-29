from app.checks.base import (
    CheckFinding,
    CheckIdentifier,
    EvidenceConfidence,
    synthesize_overall_confidence,
)


def test_synthesize_marker_is_high():
    f = CheckFinding(
        task_id="t1",
        worker_id="w1",
        check_identifier=CheckIdentifier.MARKER,
        finding_type="exact_marker_leak",
        evidence_confidence=EvidenceConfidence.HIGH,
        explanation="Marker found",
    )
    assert synthesize_overall_confidence([f]) == EvidenceConfidence.HIGH


def test_synthesize_top1_pct_and_near_copy_is_high():
    f_sim = CheckFinding(
        task_id="t1",
        worker_id="w1",
        check_identifier=CheckIdentifier.SIMILARITY,
        finding_type="model_reference_top_percentile",
        evidence_confidence=EvidenceConfidence.MEDIUM,
        explanation="Top 1%",
        numerical_measurements={"peer_percentile": 99.5},
    )
    f_dup = CheckFinding(
        task_id="t1",
        worker_id="w1",
        check_identifier=CheckIdentifier.DUPLICATES,
        finding_type="cross_worker_near_duplicate",
        evidence_confidence=EvidenceConfidence.MEDIUM,
        explanation="Near duplicate",
    )
    assert synthesize_overall_confidence([f_sim, f_dup]) == EvidenceConfidence.HIGH


def test_synthesize_top1_pct_alone_is_medium():
    f_sim = CheckFinding(
        task_id="t1",
        worker_id="w1",
        check_identifier=CheckIdentifier.SIMILARITY,
        finding_type="model_reference_top_percentile",
        evidence_confidence=EvidenceConfidence.MEDIUM,
        explanation="Top 1%",
        numerical_measurements={"peer_percentile": 99.2},
    )
    assert synthesize_overall_confidence([f_sim]) == EvidenceConfidence.MEDIUM


def test_synthesize_speed_alone_is_low():
    f_speed = CheckFinding(
        task_id="t1",
        worker_id="w1",
        check_identifier=CheckIdentifier.SPEED,
        finding_type="implausible_typing_velocity",
        evidence_confidence=EvidenceConfidence.LOW,
        explanation="Fast typing",
    )
    assert synthesize_overall_confidence([f_speed]) == EvidenceConfidence.LOW
