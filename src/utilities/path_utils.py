# utilities/path_utils.py
# System
import os
import sys
import unicodedata
import hashlib

#local
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


# Add to src/utilities/path_utils.py

def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource.
    Works for both development and PyInstaller --onefile builds.
    PyInstaller extracts bundled files to sys._MEIPASS at runtime.

    Usage:
        from utilities.path_utils import resource_path
        path = resource_path("version_info.txt")
        path = resource_path("utilities/some_file.txt")
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)