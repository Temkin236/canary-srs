import hashlib
import re
import secrets
from typing import Tuple


def generate_secret_token() -> Tuple[str, str]:
    """
    Generates a cryptographically random audit secret token with at least 256 bits of entropy.
    Returns:
        (raw_token, token_hash):
        - raw_token: Displayed once to the user for secret results link.
        - token_hash: SHA-256 digest stored safely in the database.
    """
    # 32 bytes of secure entropy => 256 bits
    raw_token = "cnry_sec_" + secrets.token_urlsafe(32)
    token_hash = hash_secret_token(raw_token)
    return raw_token, token_hash


def hash_secret_token(raw_token: str) -> str:
    """Computes deterministic SHA-256 hash of a secret token for database lookup."""
    return hashlib.sha256(raw_token.strip().encode("utf-8")).hexdigest()


def sanitize_csv_field(val: str) -> str:
    """
    Prevents CSV Formula Injection (Spreadsheet Macro Injection).
    If a field begins with '=', '+', '-', '@', '\t', or '\r', prefix with single quote "'".
    """
    if not isinstance(val, str):
        return str(val)
    if val and val[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{val}"
    return val


def sanitize_filename(filename: str) -> str:
    """Strips path traversal sequences and returns a safe basename."""
    cleaned = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", filename)
    return cleaned.strip("._")
