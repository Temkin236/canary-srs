import re
import secrets
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.schemas.marker import ManifestItem, MarkerManifestSchema, PreparedTaskOutput, TaskInput

ZW_ZERO = "\u200b"  # Zero-width space represents binary 0
ZW_ONE = "\u200c"  # Zero-width non-joiner represents binary 1
ZW_SEP = "\u200d"  # Zero-width joiner represents byte delimiter


def generate_marker_token() -> str:
    """Generates a cryptographically random, unusual canary marker token."""
    rand_hex = secrets.token_hex(5)  # 10 hex characters
    return f"cnry_{rand_hex}"


def encode_zero_width(token: str) -> str:
    """Encodes an ASCII token string into an invisible zero-width Unicode sequence."""
    encoded_chars = []
    for char in token:
        bits = f"{ord(char):08b}"
        zw_bits = "".join(ZW_ONE if b == "1" else ZW_ZERO for b in bits)
        encoded_chars.append(zw_bits)
    return ZW_SEP.join(encoded_chars) + ZW_SEP


def decode_zero_width(text: str) -> Optional[str]:
    """Decodes an invisible zero-width Unicode sequence back to an ASCII string."""
    pattern = f"([{ZW_ZERO}{ZW_ONE}]+{ZW_SEP})"
    segments = re.findall(pattern, text)
    if not segments:
        return None

    chars = []
    for seg in segments:
        clean_bits = seg.replace(ZW_SEP, "")
        if len(clean_bits) == 8:
            byte_val = int("".join("1" if c == ZW_ONE else "0" for c in clean_bits), 2)
            chars.append(chr(byte_val))

    decoded = "".join(chars)
    return decoded if decoded.startswith("cnry_") else None


def prepare_task_with_marker(
    task: TaskInput,
    hiding_method: str = "zero_width",
    custom_marker: Optional[str] = None,
) -> PreparedTaskOutput:
    """
    Embeds a unique canary marker into a task prompt using the chosen hiding method.
    Returns:
        PreparedTaskOutput containing visible and model-received previews.
    """
    marker = custom_marker or generate_marker_token()
    prompt = task.prompt.strip()

    if hiding_method == "zero_width":
        zw_payload = encode_zero_width(marker)
        # Inject invisibly near the middle or end of prompt
        prepared_prompt = f"{prompt} {zw_payload}"
        visible_preview = prompt
        model_received_preview = f"{prompt} [Hidden Zero-Width Sequence: {marker}]"
    else:  # prompt_embedded
        footnote = f"\n\n[Canary verification note: {marker}]"
        prepared_prompt = f"{prompt}{footnote}"
        visible_preview = prepared_prompt
        model_received_preview = prepared_prompt

    return PreparedTaskOutput(
        task_id=task.task_id,
        prompt=prompt,
        marker=marker,
        hiding_method=hiding_method,
        prepared_prompt=prepared_prompt,
        visible_preview=visible_preview,
        model_received_preview=model_received_preview,
    )


def generate_marker_manifest(prepared_tasks: List[PreparedTaskOutput]) -> MarkerManifestSchema:
    """Builds a versioned Marker Manifest data structure."""
    return MarkerManifestSchema(
        format_version="1.0",
        created_at=datetime.now(timezone.utc).isoformat(),
        items=[
            ManifestItem(
                task_id=t.task_id,
                marker=t.marker,
                hiding_method=t.hiding_method,
                prompt=t.prompt,
            )
            for t in prepared_tasks
        ],
    )


def validate_manifest(manifest_dict: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validates an uploaded marker manifest for schema correctness."""
    if not isinstance(manifest_dict, dict):
        return False, "Manifest must be a JSON object."
    if "items" not in manifest_dict or not isinstance(manifest_dict["items"], list):
        return False, "Manifest must contain an 'items' array."
    for idx, item in enumerate(manifest_dict["items"]):
        if not isinstance(item, dict):
            return False, f"Manifest item at index {idx} is not an object."
        if "task_id" not in item or "marker" not in item:
            return False, f"Manifest item at index {idx} is missing 'task_id' or 'marker'."
    return True, None
