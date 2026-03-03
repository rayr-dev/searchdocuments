# utilities/path_utils.py
# System
import os
import sys
import json
import unicodedata
import hashlib
import logging

#local
from utilities.logging_setup import diag


def normalize_path(path: str) -> str:
    """
    Normalize paths for consistent comparison.
    """
    diag(f"Normalizing path: {path}")
    return os.path.normpath(os.path.abspath(path))

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)
    return path

def safe_join(base: str, *paths: str) -> str:
    base = normalize_path(base)
    final = normalize_path(os.path.join(base, *paths))

    if not final.startswith(base):
        raise ValueError(f"Unsafe path detected: {final}")
    diag(f"Safe_Join: {final}")
    return final

def clean_filename(name: str) -> str:
    """
    Normalize filename to a safe, comparable form.
    """
    if not isinstance(name, str):
        name = str(name)
    name = unicodedata.normalize("NFC", name)
    diag(f"Clean Filename - {name.strip()}")
    return name.strip()

def long_path(path: str) -> str:
    path = normalize_path(path)
    if not path.startswith("\\\\?\\"):
        return "\\\\?\\" + path
    diag("Long_Path: {path}")
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

    diag(f"File_Hash: {h.hexdigest()}")
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
    diag(f"Resource Path: {relative_path}")
    return os.path.join(os.path.abspath("."), relative_path)

def get_version() -> str:
    """Read version from version_info.txt."""
    try:
        version_path = resource_path("app_version.json")
        with open(version_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            diag(f"Version: {data['version']}")
            return data.get("version", "Unknown")
    except Exception as error:
        logging.error(f"Get Version Exception: {error}")
        return "Unknown"


def get_version_info() -> dict:
    """Read full version info from version_info.txt."""
    try:
        version_path = resource_path("app_version.json")
        with open(version_path, "r", encoding="utf-8") as f:
            diag(f"Version: {f.readline()}")
            return json.load(f)
    except Exception as error:
        diag(f"Version: {error}")
        logging.error(f"Version: {error}")
        return {
            "version": "Unknown",
            "build": "Unknown",
            "author": "Unknown",
            "description": "Unknown",
            "release": "Unknown"
        }
