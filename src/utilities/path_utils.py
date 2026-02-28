import os
import unicodedata
import hashlib
from utilities.logging_setup import diag

def normalize_path(path: str) -> str:
    """
    Normalize paths for consistent comparison.
    """
    return os.path.normpath(os.path.abspath(path))

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)
    return path

def safe_join(base: str, *paths: str) -> str:
    base = normalize_path(base)
    final = normalize_path(os.path.join(base, *paths))

    if not final.startswith(base):
        raise ValueError(f"Unsafe path detected: {final}")

    return final

def clean_filename(name: str) -> str:
    """
    Normalize filename to a safe, comparable form.
    """
    if not isinstance(name, str):
        name = str(name)
    name = unicodedata.normalize("NFC", name)
    return name.strip()

def long_path(path: str) -> str:
    path = normalize_path(path)
    if not path.startswith("\\\\?\\"):
        return "\\\\?\\" + path
    return path

def file_hash(path: str) -> str:
    """
    Compute SHA-256 hash of a file.
    """
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
    except Exception as e:
        diag(f"Hash failed for: {path} ({e})")
        return None

    return h.hexdigest()
	