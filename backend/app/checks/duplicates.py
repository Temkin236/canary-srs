import re
from collections import defaultdict
from typing import Any, Dict, List, Set, Tuple

from app.checks.base import CheckFinding, CheckIdentifier, EvidenceConfidence


def normalize_text(text: str) -> str:
    """Normalizes whitespace and removes punctuation for exact duplicate comparison."""
    clean = re.sub(r"[^\w\s]", "", text.lower())
    return re.sub(r"\s+", " ", clean).strip()


def get_token_ngrams(text: str, n: int = 3) -> Set[str]:
    """Generates token n-grams (shingles) for Jaccard near-duplicate comparison."""
    tokens = re.findall(r"\b\w+\b", text.lower())
    if len(tokens) < n:
        return {" ".join(tokens)} if tokens else set()
    return {" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


def jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    """Computes Jaccard set similarity coefficient."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return intersection / union if union > 0 else 0.0


def find_matching_excerpt(text_a: str, text_b: str, min_words: int = 4) -> str:
    """Finds a common phrase shared between two answers for evidence citation."""
    words_a = text_a.split()
    for w_len in range(min(12, len(words_a)), min_words - 1, -1):
        for i in range(len(words_a) - w_len + 1):
            phrase = " ".join(words_a[i : i + w_len])
            if phrase.lower() in text_b.lower():
                return f'"{phrase}"'
    return text_a[:100] + ("..." if len(text_a) > 100 else "")


def run_duplicate_check_for_task(
    task_id: str,
    answers: List[Dict[str, Any]],  # [{"id": str, "worker_id": str, "answer": str}]
    near_dup_threshold: float = 0.80,
) -> List[CheckFinding]:
    """
    Detects exact and near-duplicate answers between distinct workers for the same task.
    Uses an inverted index for candidate generation to support up to 10,000 answers efficiently.
    Requirements FR-23 through FR-26.
    """
    findings: List[CheckFinding] = []
    if len(answers) < 2:
        return findings

    # Step 1: Exact Duplicates via Hash Grouping
    normalized_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for ans in answers:
        norm = normalize_text(ans["answer"])
        if len(norm) >= 15:  # Ignore trivial single-word responses
            normalized_groups[norm].append(ans)

    flagged_pairs: Set[Tuple[str, str]] = set()

    for norm_text, group in normalized_groups.items():
        distinct_workers = {a["worker_id"] for a in group}
        if len(distinct_workers) > 1:
            # Pairwise exact matches across distinct workers
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    a1 = group[i]
                    a2 = group[j]
                    if a1["worker_id"] != a2["worker_id"]:
                        pair_key = tuple(sorted([a1["id"], a2["id"]]))
                        flagged_pairs.add(pair_key)
                        findings.append(
                            CheckFinding(
                                task_id=task_id,
                                worker_id=a1["worker_id"],
                                check_identifier=CheckIdentifier.DUPLICATES,
                                finding_type="cross_worker_exact_duplicate",
                                evidence_confidence=EvidenceConfidence.MEDIUM,
                                explanation=(
                                    f"Exact duplicate response shared with worker "
                                    f"'{a2['worker_id']}' on the same task."
                                ),
                                evidence_text=a1["answer"][:140],
                                numerical_measurements={
                                    "jaccard_similarity": 1.0,
                                    "match_type": "exact",
                                },
                                related_answer_ids=[a2["id"]],
                            )
                        )

    # Step 2: Near-Duplicates via Inverted Index Candidate Generation (FR-25)
    shingle_cache: Dict[str, Set[str]] = {}
    inverted_index: Dict[str, List[int]] = defaultdict(list)

    for idx, ans in enumerate(answers):
        shingles = get_token_ngrams(ans["answer"], n=3)
        shingle_cache[ans["id"]] = shingles
        for s in shingles:
            inverted_index[s].append(idx)

    # Generate candidate pairs that share at least 2 common shingles
    candidate_pair_counts: Dict[Tuple[int, int], int] = defaultdict(int)
    for shingle, doc_indices in inverted_index.items():
        if len(doc_indices) < 50:  # Avoid ultra-common stopwords
            for i in range(len(doc_indices)):
                for j in range(i + 1, len(doc_indices)):
                    pair = (doc_indices[i], doc_indices[j])
                    candidate_pair_counts[pair] += 1

    # Evaluate candidate pairs
    for (idx_a, idx_b), common_count in candidate_pair_counts.items():
        if common_count < 2:
            continue

        ans_a = answers[idx_a]
        ans_b = answers[idx_b]

        if ans_a["worker_id"] == ans_b["worker_id"]:
            continue

        pair_key = tuple(sorted([ans_a["id"], ans_b["id"]]))
        if pair_key in flagged_pairs:
            continue  # Already flagged as exact

        sim = jaccard_similarity(shingle_cache[ans_a["id"]], shingle_cache[ans_b["id"]])
        if sim >= near_dup_threshold:
            flagged_pairs.add(pair_key)
            matching_phrase = find_matching_excerpt(ans_a["answer"], ans_b["answer"])
            findings.append(
                CheckFinding(
                    task_id=task_id,
                    worker_id=ans_a["worker_id"],
                    check_identifier=CheckIdentifier.DUPLICATES,
                    finding_type="cross_worker_near_duplicate",
                    evidence_confidence=EvidenceConfidence.MEDIUM,
                    explanation=(
                        f"Answer is {sim * 100:.1f}% similar to answer from "
                        f"worker '{ans_b['worker_id']}' on the same task "
                        "(token 3-gram Jaccard overlap)."
                    ),
                    evidence_text=matching_phrase,
                    numerical_measurements={
                        "jaccard_similarity": round(sim, 3),
                        "match_type": "near_duplicate",
                    },
                    related_answer_ids=[ans_b["id"]],
                    limitations=(
                        "Near-duplicate alone is medium confidence; could reflect template reuse."
                    ),
                )
            )

    return findings
