import os
import shutil
import uuid
from pathlib import Path

from app.core.config import settings
from app.core.security import sanitize_filename


def save_uploaded_file(file_obj, original_filename: str) -> str:
    """
    Saves an uploaded file to the configured storage path using an internal UUID4.
    The original filename is sanitized for logging/metadata, but NEVER used as the filesystem path.
    Returns:
        The absolute path to the safely stored file.
    """
    safe_orig = sanitize_filename(original_filename)
    extension = Path(safe_orig).suffix.lower()
    if extension not in (".csv", ".jsonl", ".json", ".txt"):
        extension = ".dat"

    internal_filename = f"{uuid.uuid4().hex}{extension}"
    target_path = os.path.join(settings.STORAGE_PATH, internal_filename)

    # Ensure parent directory exists
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)

    with open(target_path, "wb") as buffer:
        if hasattr(file_obj, "read"):
            shutil.copyfileobj(file_obj, buffer)
        elif isinstance(file_obj, (bytes, bytearray)):
            buffer.write(file_obj)
        else:
            buffer.write(str(file_obj).encode("utf-8"))

    return target_path


def delete_stored_file(filepath: str) -> bool:
    """Safely deletes an internally stored file."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    except Exception:
        pass
    return False
