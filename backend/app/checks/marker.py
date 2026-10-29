import re
from typing import Any, Dict, Optional

from app.services.marker_gen import decode_zero_width


def levenshtein_distance(s1: str, s2: str) -> int:
    """Computes Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def extract_context(text: str, start: int, end: int, window: int = 35) -> str:
    """Extracts a readable context snippet around a detected character span."""
    pre_start = max(0, start - window)
    post_end = min(len(text), end + window)
    prefix = "..." if pre_start > 0 else ""
    suffix = "..." if post_end < len(text) else ""
    return f"{prefix}{text[pre_start:post_end]}{suffix}"


def detect_marker_in_text(
    answer: str,
    target_marker: str,
    max_typo_distance: int = 1,
) -> Optional[Dict[str, Any]]:
    """
    Checks an answer text for presence of a specific canary marker.
    Matches in prioritized order:
    1. Zero-width decoded marker
    2. Exact substring match
    3. Case-insensitive match
    4. Whitespace-normalized match
    5. Bounded typo distance match (Levenshtein)

    Returns:
        Dict with match details or None if no match found.
    """
    if not answer or not target_marker:
        return None

    clean_marker = target_marker.strip()
    marker_len = len(clean_marker)

    # 1. Zero-width hidden sequence check
    decoded_zw = decode_zero_width(answer)
    if decoded_zw and decoded_zw == clean_marker:
        return {
            "finding_type": "zero_width_marker_echo",
            "match_method": "zero_width_decoded",
            "edit_distance": 0,
            "evidence_text": "[Hidden zero-width marker sequence recovered]",
            "evidence_offsets": [0, len(answer)],
            "explanation": (
                f"Hidden zero-width Unicode marker '{clean_marker}' was decoded from answer text."
            ),
        }

    # 2. Exact match
    exact_idx = answer.find(clean_marker)
    if exact_idx != -1:
        end_idx = exact_idx + marker_len
        return {
            "finding_type": "exact_marker_echo",
            "match_method": "exact",
            "edit_distance": 0,
            "evidence_text": extract_context(answer, exact_idx, end_idx),
            "evidence_offsets": [exact_idx, end_idx],
            "explanation": f"Exact canary marker '{clean_marker}' detected in worker response.",
        }

    # 3. Case-insensitive match
    lower_answer = answer.lower()
    lower_marker = clean_marker.lower()
    case_idx = lower_answer.find(lower_marker)
    if case_idx != -1:
        end_idx = case_idx + marker_len
        found_slice = answer[case_idx:end_idx]
        return {
            "finding_type": "case_normalized_marker_echo",
            "match_method": "case_insensitive",
            "edit_distance": 0,
            "evidence_text": extract_context(answer, case_idx, end_idx),
            "evidence_offsets": [case_idx, end_idx],
            "explanation": (
                f"Marker '{found_slice}' detected with differing case (expected '{clean_marker}')."
            ),
        }

    # 4. Whitespace-normalized match
    # e.g., if token was split across newline or space: "cnry_ 7f8a9b2c"
    collapsed_answer = re.sub(r"\s+", "", lower_answer)
    collapsed_marker = re.sub(r"\s+", "", lower_marker)
    if collapsed_marker in collapsed_answer:
        return {
            "finding_type": "whitespace_normalized_marker_echo",
            "match_method": "whitespace_normalized",
            "edit_distance": 0,
            "evidence_text": extract_context(answer, 0, min(100, len(answer))),
            "evidence_offsets": [0, len(answer)],
            "explanation": f"Canary marker '{clean_marker}' matched after whitespace collapsed.",
        }

    # 5. Bounded typo matching (token-level)
    # Tokens matching length bounds (+/- 2 characters)
    tokens = re.findall(r"\b[A-Za-z0-9_\-]{6,30}\b", answer)
    for token in tokens:
        if abs(len(token) - marker_len) <= max_typo_distance:
            dist = levenshtein_distance(token.lower(), lower_marker)
            if 0 < dist <= max_typo_distance:
                token_idx = answer.find(token)
                end_idx = token_idx + len(token) if token_idx != -1 else len(token)
                return {
                    "finding_type": "bounded_typo_marker_echo",
                    "match_method": "bounded_typo",
                    "edit_distance": dist,
                    "evidence_text": extract_context(answer, max(0, token_idx), end_idx),
                    "evidence_offsets": [token_idx, end_idx]
                    if token_idx != -1
                    else [0, len(token)],
                    "explanation": (
                        f"Approximate marker '{token}' detected with edit distance {dist} "
                        f"from expected '{clean_marker}'."
                    ),
                }

    return None
