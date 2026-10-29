from app.checks.base import CheckIdentifier, EvidenceConfidence
from app.checks.similarity import (
    compute_tfidf_similarities,
    run_similarity_check_for_task,
)


def test_compute_tfidf_similarities_basic():
    targets = ["The quick brown fox jumps over the lazy dog."]
    references = [
        "The quick brown fox leaps over a lazy dog.",
        "Completely unrelated text about astrophysics and dark matter.",
    ]
    sim = compute_tfidf_similarities(targets, references)
    assert sim.shape == (1, 2)
    assert sim[0][0] > 0.5  # High lexical overlap
    assert sim[0][1] < 0.2  # Low overlap


def test_similarity_check_small_group_guard():
    # Group size < 5 should not emit percentile-based findings (FR-22)
    answers = [
        {"id": "a1", "worker_id": "w1", "answer": "The quick brown fox jumps over the lazy dog."},
        {"id": "a2", "worker_id": "w2", "answer": "A totally different response."},
    ]
    references = [
        {"provider": "synthetic", "model_name": "test-v1", "reference_text": "The quick brown fox."}
    ]
    findings = run_similarity_check_for_task("task-1", answers, references)
    assert len(findings) == 0


def test_similarity_check_high_percentile():
    # Group size >= 5 with an answer very close to model reference
    ref_text = "The machine learning algorithm optimizes loss functions across training epochs."
    answers = [
        {
            "id": f"ans_{i}",
            "worker_id": f"w_{i}",
            "answer": f"Distinct human response {i} discussing diverse topics in psychology.",
        }
        for i in range(30)
    ]
    # Add outlier identical to reference
    answers.append(
        {
            "id": "ans_target",
            "worker_id": "w_target",
            "answer": ref_text,
        }
    )

    references = [{"provider": "synthetic", "model_name": "test-v1", "reference_text": ref_text}]

    findings = run_similarity_check_for_task("task-ml", answers, references)
    assert len(findings) > 0
    target_finding = next(f for f in findings if f.worker_id == "w_target")
    assert target_finding.check_identifier == CheckIdentifier.SIMILARITY
    assert target_finding.evidence_confidence in (EvidenceConfidence.MEDIUM, EvidenceConfidence.LOW)
    assert target_finding.numerical_measurements["peer_percentile"] >= 90.0
