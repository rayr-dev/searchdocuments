# tests/test_text_writer.py

import os
import pytest
from unittest.mock import MagicMock
from src.writers.text_writer import write_text_output

# -----------------------------
# Helper fixtures
# -----------------------------
@pytest.fixture
def sample_files(tmp_path):
    """Create real sample files for testing."""
    fileA = tmp_path / "fileA.txt"
    fileB = tmp_path / "fileB.txt"
    fileA.write_text("content A")
    fileB.write_text("content B")
    return str(fileA), str(fileB), str(tmp_path)

def read_txt(path):
    """Helper to read text file contents."""
    with open(path, encoding="utf-8") as f:
        return f.read()

# -----------------------------
# Basic output tests
# -----------------------------
def test_txt_file_is_created(tmp_path):
    write_text_output(str(tmp_path), [], [], [])
    assert os.path.exists(str(tmp_path / "comparison.txt"))

def test_txt_has_section_headers(tmp_path):
    write_text_output(str(tmp_path), [], [], [])
    content = read_txt(str(tmp_path / "comparison.txt"))
    assert "=== Exact Matches ===" in content
    assert "=== Mismatches ===" in content
    assert "=== Missing in Folder B ===" in content

def test_txt_empty_data_has_only_headers(tmp_path):
    write_text_output(str(tmp_path), [], [], [])
    content = read_txt(str(tmp_path / "comparison.txt"))
    lines = [line for line in content.splitlines() if line.strip()]
    assert len(lines) == 7 # 4 count lines + 3 section headers

# -----------------------------
# Matches tests
# -----------------------------
def test_txt_writes_exact_match(sample_files):
    fileA, fileB, output_dir = sample_files
    matches = [("file.txt", fileA, fileB, None)]
    write_text_output(output_dir, matches, [], [])
    content = read_txt(os.path.join(output_dir, "comparison.txt"))
    assert "file.txt" in content
    assert fileA in content
    assert fileB in content

def test_txt_writes_multiple_matches(sample_files):
    fileA, fileB, output_dir = sample_files
    matches = [
        ("file1.txt", fileA, fileB, None),
        ("file2.txt", fileA, fileB, None),
    ]
    write_text_output(output_dir, matches, [], [])
    content = read_txt(os.path.join(output_dir, "comparison.txt"))
    assert "file1.txt" in content
    assert "file2.txt" in content

def test_txt_skips_match_with_invalid_pathA(tmp_path):
    fileB = tmp_path / "fileB.txt"
    fileB.write_text("content")
    matches = [("file.txt", "fake/path.txt", str(fileB), None)]
    write_text_output(str(tmp_path), matches, [], [])
    content = read_txt(str(tmp_path / "comparison.txt"))
    assert "file.txt" not in content

def test_txt_skips_match_with_invalid_pathB(tmp_path):
    fileA = tmp_path / "fileA.txt"
    fileA.write_text("content")
    matches = [("file.txt", str(fileA), "fake/pathB.txt", None)]
    write_text_output(str(tmp_path), matches, [], [])
    content = read_txt(str(tmp_path / "comparison.txt"))
    assert "file.txt" not in content

# -----------------------------
# Mismatches tests
# -----------------------------
def test_txt_writes_mismatch(sample_files):
    fileA, fileB, output_dir = sample_files
    mismatched = [("file.txt", fileA, [(fileB, 100, 1234567890.0)], None)]
    write_text_output(output_dir, [], mismatched, [])
    content = read_txt(os.path.join(output_dir, "comparison.txt"))
    assert "file.txt" in content
    assert "=== Mismatches ===" in content

def test_txt_writes_multiple_mismatch_candidates(sample_files):
    fileA, fileB, output_dir = sample_files
    mismatched = [("file.txt", fileA, [
        (fileB, 100, 1234567890.0),
        (fileB, 200, 1234567891.0),
    ], None)]
    write_text_output(output_dir, [], mismatched, [])
    content = read_txt(os.path.join(output_dir, "comparison.txt"))
    assert content.count("B:") >= 2

def test_txt_skips_mismatch_with_invalid_pathA(tmp_path):
    fileB = tmp_path / "fileB.txt"
    fileB.write_text("content")
    mismatched = [("file.txt", "fake/path.txt", [(str(fileB), 100, 0)], None)]
    write_text_output(str(tmp_path), [], mismatched, [])
    content = read_txt(str(tmp_path / "comparison.txt"))
    assert "file.txt" not in content

def test_txt_skips_mismatch_with_invalid_pathB(tmp_path):
    fileA = tmp_path / "fileA.txt"
    fileA.write_text("content")
    mismatched = [("file.txt", str(fileA), [("fake/pathB.txt", 100, 0)], None)]
    write_text_output(str(tmp_path), [], mismatched, [])
    content = read_txt(str(tmp_path / "comparison.txt"))
    assert "fake/pathB.txt" not in content

def test_txt_mismatch_handles_timestamp_error(tmp_path, monkeypatch):
    """Should write empty timestamp if getmtime fails."""
    fileA = tmp_path / "fileA.txt"
    fileB = tmp_path / "fileB.txt"
    fileA.write_text("content")
    fileB.write_text("content")

    def fake_getmtime(path):
        raise OSError("Permission denied")
    monkeypatch.setattr(os.path, "getmtime", fake_getmtime)

    mismatched = [("file.txt", str(fileA), [(str(fileB), 100, None)], None)]
    write_text_output(str(tmp_path), [], mismatched, [])
    content = read_txt(str(tmp_path / "comparison.txt"))
    assert "file.txt" in content

# -----------------------------
# Missing tests
# -----------------------------
def test_txt_writes_missing(sample_files):
    fileA, fileB, output_dir = sample_files
    missing = [("file.txt", fileA)]
    write_text_output(output_dir, [], [], missing)
    content = read_txt(os.path.join(output_dir, "comparison.txt"))
    assert "file.txt" in content
    assert "=== Missing in Folder B ===" in content

def test_txt_skips_missing_with_invalid_pathA(tmp_path):
    missing = [("file.txt", "fake/path.txt")]
    write_text_output(str(tmp_path), [], [], missing)
    content = read_txt(str(tmp_path / "comparison.txt"))
    assert "file.txt" not in content

# -----------------------------
# Callback tests
# -----------------------------
def test_txt_status_callback_called(tmp_path):
    status_mock = MagicMock()
    write_text_output(str(tmp_path), [], [], [], status_callback=status_mock)
    assert status_mock.called

def test_txt_progress_callback_called(tmp_path):
    progress_mock = MagicMock()
    write_text_output(str(tmp_path), [], [], [], progress_callback=progress_mock)
    progress_mock.assert_called_with(85)

# -----------------------------
# Error handling tests
# -----------------------------
def test_txt_handles_write_error(tmp_path, monkeypatch):
    """Should handle file write errors gracefully."""
    def fake_open(*args, **kwargs):
        raise PermissionError("Cannot write file")
    monkeypatch.setattr("builtins.open", fake_open)
    write_text_output(str(tmp_path), [], [], [])

# -----------------------------
# Combined data test
# -----------------------------
def test_txt_writes_all_types(sample_files):
    fileA, fileB, output_dir = sample_files
    matches    = [("match.txt", fileA, fileB, None)]
    mismatched = [("mismatch.txt", fileA, [(fileB, 100, 1234567890.0)], None)]
    missing    = [("missing.txt", fileA)]
    write_text_output(output_dir, matches, mismatched, missing)
    content = read_txt(os.path.join(output_dir, "comparison.txt"))
    assert "match.txt" in content
    assert "mismatch.txt" in content
    assert "missing.txt" in content

def test_txt_writes_action_for_match(sample_files):
    """Action field should appear in output when set on a match."""
    fileA, fileB, output_dir = sample_files
    matches = [("file.txt", fileA, fileB, "DELETED")]
    write_text_output(output_dir, matches, [], [])
    content = read_txt(os.path.join(output_dir, "comparison.txt"))
    assert "Action: DELETED" in content


def test_txt_writes_action_for_mismatch(sample_files):
    """Action field should appear in output when set on a mismatch."""
    fileA, fileB, output_dir = sample_files
    mismatched = [("file.txt", fileA, [(fileB, 100, 1234567890.0)], "QUARANTINED")]
    write_text_output(output_dir, [], mismatched, [])
    content = read_txt(os.path.join(output_dir, "comparison.txt"))
    assert "Action: QUARANTINED" in content

def test_txt_has_count_lines(tmp_path):
    write_text_output(str(tmp_path), [], [], [],
                      source_count=10, target_count=20,
                      source_unique=5, target_unique=8)
    content = read_txt(str(tmp_path / "comparison.txt"))
    assert "Total Files in Source:   10" in content
    assert "Total Files in Target:   20" in content
    assert "Unique Filenames Source: 5" in content
    assert "Unique Filenames Target: 8" in content

