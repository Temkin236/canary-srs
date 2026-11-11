import csv
import json
import os
from collections import defaultdict

from app.checks.base import (
    CheckFinding,
    CheckIdentifier,
    EvidenceConfidence,
    synthesize_overall_confidence,
)
from app.checks.duplicates import (
    get_token_ngrams,
    jaccard_similarity,
    normalize_text,
    run_duplicate_check_for_task,
)

FIXTURES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "fixtures"))


def test_jaccard_similarity_calculation():
    s1 = get_token_ngrams("The quick brown fox jumps over the lazy dog", n=3)
    s2 = get_token_ngrams("The quick brown fox jumps over a lazy dog", n=3)
    sim = jaccard_similarity(s1, s2)
    assert 0.3 < sim < 1.0


def test_normalize_text():
    assert normalize_text("Hello, World! 123") == "hello world 123"
    assert normalize_text("  Extra   whitespace   \n\t here. ") == "extra whitespace here"


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
    assert f.numerical_measurements["match_type"] == "exact"
    assert f.numerical_measurements["jaccard_similarity"] == 1.0


def test_cross_worker_near_duplicates():
    base_text = "Photosynthesis converts solar light energy into chemical energy stored in glucose."
    slight_mod = "Photosynthesis converts solar light energy into chemical energy stored in starch."
    answers = [
        {"id": "a1", "worker_id": "w1", "answer": base_text},
        {"id": "a2", "worker_id": "w2", "answer": slight_mod},
        {
            "id": "a3",
            "worker_id": "w3",
            "answer": "Quantum mechanics describes microscopic particles.",
        },
    ]
    findings = run_duplicate_check_for_task("task-near", answers, near_dup_threshold=0.60)
    assert len(findings) >= 1
    f = findings[0]
    assert f.check_identifier == CheckIdentifier.DUPLICATES
    assert f.finding_type == "cross_worker_near_duplicate"
    assert f.evidence_confidence == EvidenceConfidence.MEDIUM
    assert f.numerical_measurements["match_type"] == "near_duplicate"
    assert f.numerical_measurements["jaccard_similarity"] >= 0.60


def test_independent_answers_zero_findings():
    """Genuinely diverse and independent answers must produce zero duplicate findings."""
    answers = [
        {
            "id": "ans_1",
            "worker_id": "worker_alpha",
            "answer": (
                "Regular maintenance helps a solar system produce power reliably. "
                "I clean dust from panels, inspect cables, check terminals, and "
                "review charge controller readings. Keeping a log helps note changes."
            ),
        },
        {
            "id": "ans_2",
            "worker_id": "worker_beta",
            "answer": (
                "Solar setups degrade rapidly if neglected. Periodic inspections "
                "ensure photovoltaic cells are free of debris, preventing degradation. "
                "It is also crucial to verify inverter efficiency and measure voltages."
            ),
        },
    ]
    findings = run_duplicate_check_for_task("T001", answers, near_dup_threshold=0.80)
    assert len(findings) == 0, f"Expected 0 findings for independent answers, got: {findings}"


def test_clean_baseline_csv_has_zero_duplicate_findings():
    """
    Verifies that the clean baseline dataset (clean_dataset.csv) generates
    zero duplicate findings across all tasks under the standard 0.80 threshold.
    """
    csv_path = os.path.join(FIXTURES_DIR, "clean_dataset.csv")
    assert os.path.exists(csv_path), f"Clean dataset fixture not found at {csv_path}"

    tasks = defaultdict(list)
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            tasks[row["task_id"]].append(
                {
                    "id": f"row_{idx}",
                    "worker_id": row["worker_id"],
                    "answer": row["answer"],
                }
            )

    all_findings = []
    for task_id, answers in tasks.items():
        findings = run_duplicate_check_for_task(task_id, answers, near_dup_threshold=0.80)
        all_findings.extend(findings)

    assert len(all_findings) == 0, (
        f"Expected 0 duplicate findings on clean baseline, but found {len(all_findings)}"
    )


def test_clean_baseline_jsonl_has_zero_duplicate_findings():
    """Verifies that clean_dataset.jsonl generates zero duplicate findings."""
    jsonl_path = os.path.join(FIXTURES_DIR, "clean_dataset.jsonl")
    assert os.path.exists(jsonl_path), f"Clean JSONL fixture not found at {jsonl_path}"

    tasks = defaultdict(list)
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if line.strip():
                row = json.loads(line)
                tasks[row["task_id"]].append(
                    {
                        "id": f"row_{idx}",
                        "worker_id": row["worker_id"],
                        "answer": row["answer"],
                    }
                )

    all_findings = []
    for task_id, answers in tasks.items():
        findings = run_duplicate_check_for_task(task_id, answers, near_dup_threshold=0.80)
        all_findings.extend(findings)

    assert len(all_findings) == 0


def test_duplicate_dataset_fixture_expected_findings():
    """
    Verifies that the intentionally duplicated dataset (duplicate_dataset.csv)
    correctly triggers exact and near duplicate detections on duplicate tasks,
    while producing no false positives on sub-threshold or independent tasks.
    """
    csv_path = os.path.join(FIXTURES_DIR, "duplicate_dataset.csv")
    assert os.path.exists(csv_path), f"Duplicate dataset fixture not found at {csv_path}"

    tasks = defaultdict(list)
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            tasks[row["task_id"]].append(
                {
                    "id": f"row_{idx}",
                    "worker_id": row["worker_id"],
                    "answer": row["answer"],
                }
            )

    # T001: Exact duplicate
    findings_t1 = run_duplicate_check_for_task("T001", tasks["T001"], near_dup_threshold=0.80)
    assert len(findings_t1) == 1
    assert findings_t1[0].finding_type == "cross_worker_exact_duplicate"
    assert findings_t1[0].numerical_measurements["match_type"] == "exact"

    # T002: Near duplicate (>= 0.80)
    findings_t2 = run_duplicate_check_for_task("T002", tasks["T002"], near_dup_threshold=0.80)
    assert len(findings_t2) == 1
    assert findings_t2[0].finding_type == "cross_worker_near_duplicate"
    assert findings_t2[0].numerical_measurements["match_type"] == "near_duplicate"

    # T003: Sub-threshold (~50%, should NOT flag)
    findings_t3 = run_duplicate_check_for_task("T003", tasks["T003"], near_dup_threshold=0.80)
    assert len(findings_t3) == 0

    # T006: Independent answers (should NOT flag)
    findings_t6 = run_duplicate_check_for_task("T006", tasks["T006"], near_dup_threshold=0.80)
    assert len(findings_t6) == 0


def test_similar_answers_to_different_tasks():
    """
    Task Grouping Invariant:
    Duplicate detection is scoped strictly per task_id.
    Identical or similar text across DIFFERENT task IDs must never produce duplicate findings.
    """
    identical_text = (
        "This is an identical generic response submitted to two completely different questions "
        "by two different workers."
    )
    task_a_answers = [{"id": "a1", "worker_id": "worker_x", "answer": identical_text}]
    task_b_answers = [{"id": "b1", "worker_id": "worker_y", "answer": identical_text}]

    # In Canary SRS, duplicate checking is run per task_id group
    findings_a = run_duplicate_check_for_task("task_alpha", task_a_answers)
    findings_b = run_duplicate_check_for_task("task_beta", task_b_answers)

    assert len(findings_a) == 0
    assert len(findings_b) == 0


def test_confidence_classification_precedence():
    """
    Verifies confidence classification for duplicate findings under FR-29:
    - Near-copy duplicate alone: Medium confidence
    - Exact duplicate alone: Medium confidence
    - Near-copy duplicate + Top 1% model similarity: High confidence
    - Duplicate + Marker hit: High confidence
    """
    dup_finding = CheckFinding(
        task_id="t1",
        worker_id="w1",
        check_identifier=CheckIdentifier.DUPLICATES,
        finding_type="cross_worker_near_duplicate",
        evidence_confidence=EvidenceConfidence.MEDIUM,
        explanation="Near-duplicate shared with another worker.",
    )
    # 1. Duplicate alone -> Medium
    assert synthesize_overall_confidence([dup_finding]) == EvidenceConfidence.MEDIUM

    # 2. Duplicate + Top 1% similarity -> High
    sim_finding_top1 = CheckFinding(
        task_id="t1",
        worker_id="w1",
        check_identifier=CheckIdentifier.SIMILARITY,
        finding_type="high_model_similarity",
        evidence_confidence=EvidenceConfidence.MEDIUM,
        explanation="High similarity to reference.",
        numerical_measurements={"peer_percentile": 99.5},
    )
    assert synthesize_overall_confidence([dup_finding, sim_finding_top1]) == EvidenceConfidence.HIGH

    # 3. Duplicate + Marker hit -> High
    marker_finding = CheckFinding(
        task_id="t1",
        worker_id="w1",
        check_identifier=CheckIdentifier.MARKER,
        finding_type="marker_hit",
        evidence_confidence=EvidenceConfidence.HIGH,
        explanation="Canary marker detected.",
    )
    assert synthesize_overall_confidence([dup_finding, marker_finding]) == EvidenceConfidence.HIGH
