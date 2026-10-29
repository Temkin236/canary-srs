from app.core.security import (
    generate_secret_token,
    hash_secret_token,
    sanitize_csv_field,
    sanitize_filename,
)


def test_secret_token_entropy_and_hash():
    token1, hash1 = generate_secret_token()
    token2, hash2 = generate_secret_token()

    # Must be distinct (at least 256 bits entropy)
    assert token1 != token2
    assert hash1 != hash2
    assert token1.startswith("cnry_sec_")
    assert len(hash1) == 64  # SHA-256 hex digest length

    # Hashing must be deterministic
    assert hash_secret_token(token1) == hash1
    assert hash_secret_token(token2) == hash2


def test_sanitize_csv_formula_injection():
    # Dangerous formula prefixes must be prepended with a single quote
    assert sanitize_csv_field("=SUM(A1:A10)") == "'=SUM(A1:A10)"
    assert sanitize_csv_field("+cmd|' /C calc'!A0") == "'+cmd|' /C calc'!A0"
    assert sanitize_csv_field("-123") == "'-123"
    assert sanitize_csv_field("@malicious") == "'@malicious"
    assert sanitize_csv_field("\talert") == "'\talert"

    # Benign text should remain unmodified
    assert sanitize_csv_field("Normal text response") == "Normal text response"
    assert sanitize_csv_field("12345") == "12345"


def test_sanitize_filename_path_traversal():
    assert sanitize_filename("../../etc/passwd") == "etc_passwd"
    assert sanitize_filename("safe_file.csv") == "safe_file.csv"
