from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class CheckIdentifier(str, Enum):
    MARKER = "marker"
    SIMILARITY = "similarity"
    DUPLICATES = "duplicates"
    SPEED = "speed"


class EvidenceConfidence(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class CheckFinding:
    task_id: str
    worker_id: str
    check_identifier: CheckIdentifier
    finding_type: str
    evidence_confidence: EvidenceConfidence
    explanation: str
    evidence_text: Optional[str] = None
    evidence_offsets: Optional[List[int]] = None  # [start, end]
    numerical_measurements: Dict[str, Any] = field(default_factory=dict)
    related_answer_ids: List[str] = field(default_factory=list)
    limitations: str = "Evidence for human review only; does not prove AI authorship or cheating."


def synthesize_overall_confidence(
    findings_for_answer: List[CheckFinding],
) -> EvidenceConfidence:
    """
    Synthesizes overall evidence confidence according to FR-29 precedence rules:
    - Marker hit: High
    - Top 1% model similarity + near-copy: High
    - Top 1% model similarity alone: Medium
    - Near-copy duplicate alone: Medium
    - Speed anomaly alone: Low
    - Top 5% model similarity alone: Low
    """
    has_marker = any(f.check_identifier == CheckIdentifier.MARKER for f in findings_for_answer)
    has_near_copy = any(
        f.check_identifier == CheckIdentifier.DUPLICATES
        and f.finding_type == "cross_worker_near_duplicate"
        for f in findings_for_answer
    )
    has_top_1_pct = any(
        f.check_identifier == CheckIdentifier.SIMILARITY
        and f.numerical_measurements.get("peer_percentile", 0) >= 99.0
        for f in findings_for_answer
    )
    has_top_5_pct = any(
        f.check_identifier == CheckIdentifier.SIMILARITY
        and f.numerical_measurements.get("peer_percentile", 0) >= 95.0
        for f in findings_for_answer
    )

    if has_marker or (has_top_1_pct and has_near_copy):
        return EvidenceConfidence.HIGH

    if has_top_1_pct or has_near_copy:
        return EvidenceConfidence.MEDIUM

    if has_top_5_pct or any(
        f.check_identifier == CheckIdentifier.SPEED for f in findings_for_answer
    ):
        return EvidenceConfidence.LOW

    # Default to highest individual finding confidence if any
    for conf in (EvidenceConfidence.HIGH, EvidenceConfidence.MEDIUM, EvidenceConfidence.LOW):
        if any(f.evidence_confidence == conf for f in findings_for_answer):
            return conf

    return EvidenceConfidence.LOW
