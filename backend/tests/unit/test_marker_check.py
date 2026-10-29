from app.checks.marker import detect_marker_in_text, levenshtein_distance
from app.services.marker_gen import encode_zero_width


def test_levenshtein_distance():
    assert levenshtein_distance("kitten", "sitting") == 3
    assert levenshtein_distance("canary", "canary") == 0
    assert levenshtein_distance("cnry_1234", "cnry_1235") == 1


def test_exact_marker_detection():
    marker = "cnry_a1b2c3d4"
    answer = f"According to the documentation {marker} we proceed with analysis."
    result = detect_marker_in_text(answer, marker)

    assert result is not None
    assert result["match_method"] == "exact"
    assert result["edit_distance"] == 0
    assert result["evidence_offsets"] == [31, 31 + len(marker)]
    assert marker in result["evidence_text"]


def test_case_insensitive_marker_detection():
    marker = "cnry_A1B2C3D4"
    answer = "Lower case text cnry_a1b2c3d4 inside answer."
    result = detect_marker_in_text(answer, marker)

    assert result is not None
    assert result["match_method"] == "case_insensitive"
    assert result["edit_distance"] == 0


def test_whitespace_normalized_marker_detection():
    marker = "cnry_99887766"
    answer = "The token is cnry_   99887766 broken by whitespace."
    result = detect_marker_in_text(answer, marker)

    assert result is not None
    assert result["match_method"] == "whitespace_normalized"


def test_bounded_typo_marker_detection():
    marker = "cnry_77665544"
    # Typo: 1 character changed ('5' -> '9')
    typo_token = "cnry_77669544"
    answer = f"The respondent echoed {typo_token} in their output."
    result = detect_marker_in_text(answer, marker, max_typo_distance=1)

    assert result is not None
    assert result["match_method"] == "bounded_typo"
    assert result["edit_distance"] == 1
    assert typo_token in result["evidence_text"]


def test_zero_width_marker_detection():
    marker = "cnry_zw_887766"
    zw_seq = encode_zero_width(marker)
    answer = f"Here is an answer containing {zw_seq} invisibly."
    result = detect_marker_in_text(answer, marker)

    assert result is not None
    assert result["match_method"] == "zero_width_decoded"


def test_no_false_positive():
    marker = "cnry_unmatched"
    answer = "A completely benign human response with no canary tokens."
    result = detect_marker_in_text(answer, marker)
    assert result is None


def test_api_prepare_endpoints(client):
    payload = {
        "tasks": [
            {"task_id": "t1", "prompt": "Prompt 1"},
            {"task_id": "t2", "prompt": "Prompt 2"},
        ],
        "hiding_method": "zero_width",
    }
    res = client.post("/api/v1/prepare/markers", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["tasks"]) == 2
    assert "manifest" in data
    assert data["tasks"][0]["marker"].startswith("cnry_")
