from app.checks.base import CheckIdentifier, EvidenceConfidence
from app.checks.duplicates import (
    get_token_ngrams,
    jaccard_similarity,
    run_duplicate_check_for_task,
)


def test_jaccard_similarity_calculation():
    s1 = get_token_ngrams("The quick brown fox jumps over the lazy dog", n=3)
    s2 = get_token_ngrams("The quick brown fox jumps over a lazy dog", n=3)
    sim = jaccard_similarity(s1, s2)
    assert 0.3 < sim < 1.0


def test_cross_worker_exact_duplicates():
    answers = [
        {
            "id": "a1",
            "worker_id": "w1",
            "answer": "This is an exact duplicate response that is long enough to trigger check.",
        },
        {
            "id": "a2",
            "worker_id": "w2",
            "answer": "This is an exact duplicate response that is long enough to trigger check.",
        },
        {
            "id": "a3",
            "worker_id": "w3",
            "answer": "Completely unique and distinct content that should not be flagged at all.",
        },
    ]
    findings = run_duplicate_check_for_task("task-dup", answers)
    assert len(findings) == 1
    f = findings[0]
    assert f.check_identifier == CheckIdentifier.DUPLICATES
    assert f.finding_type == "cross_worker_exact_duplicate"
    assert f.evidence_confidence == EvidenceConfidence.MEDIUM


def test_cross_worker_near_duplicates():
    base_text = "Photosynthesis converts solar light energy into chemical energy stored in glucose."
    slight_mod = "Photosynthesis converts solar light energy into chemical energy stored in starch."
    answers = [
        {"id": "a1", "worker_id": "w1", "answer": base_text},
        {"id": "a2", "worker_id": "w2", "answer": slight_mod},
        {"id": "a3", "worker_id": "w3", "answer": "Quantum mechanics describes particles."},
    ]
    findings = run_duplicate_check_for_task("task-near", answers, near_dup_threshold=0.60)
    assert len(findings) >= 1
    f = findings[0]
    assert f.check_identifier == CheckIdentifier.DUPLICATES
    assert f.finding_type == "cross_worker_near_duplicate"
