# tests/test_path_utils.py

import os
import pytest

from src.utilities.path_utils import (
    normalize_path,
    ensure_dir,
    safe_join,
    clean_filename,
    long_path,
    file_hash,
)

# -----------------------------
# normalize_path tests
# -----------------------------
def test_normalize_path_returns_absolute():
    result = normalize_path("some/relative/path")
    assert os.path.isabs(result)

def test_normalize_path_resolves_dots():
    result = normalize_path("some/folder/../folder/file.txt")
    assert ".." not in result

def test_normalize_path_consistent():
    # Same path expressed differently should normalize to the same result
    a = normalize_path("foo/bar")
    b = normalize_path("foo/./bar")
    assert a == b

# -----------------------------
# ensure_dir tests
# -----------------------------
def test_ensure_dir_creates_folder(tmp_path):
    new_dir = str(tmp_path / "new_folder")
    result = ensure_dir(new_dir)
    assert os.path.isdir(result)

def test_ensure_dir_returns_path(tmp_path):
    new_dir = str(tmp_path / "another_folder")
    result = ensure_dir(new_dir)
    assert result == new_dir

def test_ensure_dir_does_not_fail_if_exists(tmp_path):
    # Calling twice should not raise an error
    new_dir = str(tmp_path / "existing_folder")
    ensure_dir(new_dir)
    ensure_dir(new_dir)  # second call should be fine
    assert os.path.isdir(new_dir)

# -----------------------------
# safe_join tests
# -----------------------------
def test_safe_join_normal_path(tmp_path):
    result = safe_join(str(tmp_path), "subfolder", "file.txt")
    assert result.endswith("file.txt")

def test_safe_join_raises_on_traversal(tmp_path):
    # Attempting to escape the base directory should raise ValueError
    with pytest.raises(ValueError, match="Unsafe path detected"):
        safe_join(str(tmp_path), "..", "..", "etc", "passwd")

# -----------------------------
# clean_filename tests
# -----------------------------
def test_clean_filename_strips_whitespace():
    assert clean_filename("  myfile.txt  ") == "myfile.txt"

def test_clean_filename_handles_non_string():
    # Should convert non-strings without crashing
    result = clean_filename(12345)
    assert result == "12345"

def test_clean_filename_normalizes_unicode():
    # NFC normalized string should come back unchanged
    result = clean_filename("résumé.txt")
    assert result == "résumé.txt"

def test_clean_filename_empty_string():
    assert clean_filename("") == ""

# -----------------------------
# long_path tests
# -----------------------------
def test_long_path_adds_prefix():
    result = long_path("C:\\some\\path")
    assert result.startswith("\\\\?\\")

def test_long_path_does_not_double_prefix():
    # Calling twice should not add the prefix twice
    result = long_path("\\\\?\\C:\\some\\path")
    assert result.count("\\\\?\\") == 1

# -----------------------------
# file_hash tests
# -----------------------------
def test_file_hash_returns_string(tmp_path):
    test_file = tmp_path / "sample.txt"
    test_file.write_text("hello world")
    result = file_hash(str(test_file))
    assert isinstance(result, str)
    assert len(result) == 64  # SHA-256 is always 64 hex characters

def test_file_hash_consistent(tmp_path):
    # Same file hashed twice should return the same value
    test_file = tmp_path / "sample.txt"
    test_file.write_text("hello world")
    assert file_hash(str(test_file)) == file_hash(str(test_file))

def test_file_hash_different_contents(tmp_path):
    # Different content should produce different hashes
    file_a = tmp_path / "a.txt"
    file_b = tmp_path / "b.txt"
    file_a.write_text("hello")
    file_b.write_text("world")
    assert file_hash(str(file_a)) != file_hash(str(file_b))

def test_file_hash_returns_none_for_missing_file():
    result = file_hash("nonexistent/file/path.txt")
    assert result is None

# -----------------------------
# resource_path tests
# -----------------------------
def test_resource_path_in_dev_mode():
    """In dev mode should return path relative to cwd."""
    from src.utilities.path_utils import resource_path
    result = resource_path("version_info.txt")
    assert "version_info.txt" in result

def test_resource_path_in_frozen_mode(monkeypatch):
    """In frozen/PyInstaller mode should use sys._MEIPASS."""
    import sys
    from src.utilities.path_utils import resource_path
    monkeypatch.setattr(sys, "_MEIPASS", "/fake/meipass", raising=False)
    result = resource_path("version_info.txt")
    # Use os.path.join to handle Windows vs Linux separators
    assert result == os.path.join("/fake/meipass", "version_info.txt")

# -----------------------------
# get_version tests
# -----------------------------
def test_get_version_returns_correct_version(tmp_path, monkeypatch):
    """Should return version string from version_info.txt."""
    import json
    import builtins
    from src.utilities.path_utils import get_version

    version_file = tmp_path / "version_info.txt"
    version_file.write_text(json.dumps({
        "version": "1.0.0",
        "build": "20260301",
        "author": "Test Author",
        "description": "Test",
        "release": "Production"
    }))

    original_open = builtins.open

    def fake_open(path, *args, **kwargs):
        if "version_info.txt" in str(path):
            return original_open(str(version_file), *args, **kwargs)
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", fake_open)

    result = get_version()
    assert result == "1.0.0"

def test_get_version_returns_unknown_when_file_missing(monkeypatch):
    """Should return Unknown if version_info.txt not found."""
    from src.utilities.path_utils import get_version
    monkeypatch.setattr(
        "src.utilities.path_utils.resource_path",
        lambda x: "nonexistent/path/version_info.txt"
    )
    result = get_version()
    assert result == "Unknown"

def test_get_version_returns_unknown_when_json_invalid(tmp_path, monkeypatch):
    """Should return Unknown if version_info.txt is not valid JSON."""
    from src.utilities.path_utils import get_version

    version_file = tmp_path / "version_info.txt"
    version_file.write_text("this is not json")

    monkeypatch.setattr(
        "src.utilities.path_utils.resource_path",
        lambda x: str(version_file)
    )
    result = get_version()
    assert result == "Unknown"

# -----------------------------
# get_version_info tests
# -----------------------------
def test_get_version_info_returns_correct_dict(tmp_path, monkeypatch):
    """Should return full version info dict."""
    import json
    import builtins
    from src.utilities.path_utils import get_version_info

    expected = {
        "version": "1.0.0",
        "build": "20260301",
        "author": "Test Author",
        "description": "Test Description",
        "release": "Production"
    }

    version_file = tmp_path / "version_info.txt"
    print(f"version_file: [{version_file}]")
    version_file.write_text(json.dumps(expected))
    original_open = builtins.open
    version_file.write_text(json.dumps(expected))

    # Patch builtins.open to return our file
    original_open = builtins.open

    def fake_open(path, *args, **kwargs):
        if "version_info.txt" in str(path):
            return original_open(str(version_file), *args, **kwargs)
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", fake_open)

    result = get_version_info()
    assert result == expected

def test_get_version_info_returns_defaults_when_file_missing(monkeypatch):
    """Should return default dict if version_info.txt not found."""
    from src.utilities.path_utils import get_version_info
    monkeypatch.setattr(
        "src.utilities.path_utils.resource_path",
        lambda x: "nonexistent/path/version_info.txt"
    )
    result = get_version_info()
    assert result["version"] == "Unknown"
    assert result["build"] == "Unknown"
    assert result["author"] == "Unknown"
    assert result["description"] == "Unknown"
    assert result["release"] == "Unknown"

def test_get_version_info_returns_defaults_when_json_invalid(tmp_path, monkeypatch):
    """Should return defaults if version_info.txt is not valid JSON."""
    from src.utilities.path_utils import get_version_info

    version_file = tmp_path / "version_info.txt"
    version_file.write_text("not valid json")

    monkeypatch.setattr(
        "src.utilities.path_utils.resource_path",
        lambda x: str(version_file)
    )
    result = get_version_info()
    assert result["version"] == "Unknown"