# tests/test_csv_writer.py

import os
import csv
import pytest
from src.writers.csv_writer import write_csv_output

# -----------------------------
# Helper fixture
# -----------------------------
@pytest.fixture
def sample_files(tmp_path):
    """Create real sample files for testing."""
    fileA = tmp_path / "fileA.txt"
    fileB = tmp_path / "fileB.txt"
    fileA.write_text("content A")
    fileB.write_text("content B")
    return str(fileA), str(fileB), str(tmp_path)

def read_csv(path):
    """Helper to read CSV into list of rows."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.reader(f))

# -----------------------------
# Basic output tests
# -----------------------------
def test_csv_file_is_created(tmp_path):
    write_csv_output(str(tmp_path), [], [], [])
    assert os.path.exists(str(tmp_path / "comparison.csv"))

def test_csv_has_header_row(tmp_path):
    write_csv_output(str(tmp_path), [], [], [])
    rows = read_csv(str(tmp_path / "comparison.csv"))
    assert rows[0] == ["Status", "Filename", "Path A", "Timestamp A", "Path B", "Timestamp B"]

def test_csv_empty_data_only_header(tmp_path):
    write_csv_output(str(tmp_path), [], [], [])
    rows = read_csv(str(tmp_path / "comparison.csv"))
    assert len(rows) == 1  # only header row

# -----------------------------
# Matches tests
# -----------------------------
def test_csv_writes_exact_match(sample_files):
    fileA, fileB, output_dir = sample_files
    matches = [("file.txt", fileA, fileB)]
    write_csv_output(output_dir, matches, [], [])
    rows = read_csv(os.path.join(output_dir, "comparison.csv"))
    assert len(rows) == 2  # header + 1 match
    assert rows[1][0] == "Exact Match"
    assert rows[1][1] == "file.txt"

def test_csv_writes_multiple_matches(sample_files):
    fileA, fileB, output_dir = sample_files
    matches = [
        ("file1.txt", fileA, fileB),
        ("file2.txt", fileA, fileB),
    ]
    write_csv_output(output_dir, matches, [], [])
    rows = read_csv(os.path.join(output_dir, "comparison.csv"))
    assert len(rows) == 3  # header + 2 matches

def test_csv_skips_match_with_invalid_pathA(tmp_path):
    fileB = tmp_path / "fileB.txt"
    fileB.write_text("content")
    matches = [("file.txt", "fake/path/file.txt", str(fileB))]
    write_csv_output(str(tmp_path), matches, [], [])
    rows = read_csv(str(tmp_path / "comparison.csv"))
    assert len(rows) == 1  # only header, match skipped

def test_csv_skips_match_with_invalid_pathB(tmp_path):
    fileA = tmp_path / "fileA.txt"
    fileA.write_text("content")
    matches = [("file.txt", str(fileA), "fake/path/file.txt")]
    write_csv_output(str(tmp_path), matches, [], [])
    rows = read_csv(str(tmp_path / "comparison.csv"))
    assert len(rows) == 1  # only header, match skipped

# -----------------------------
# Mismatches tests
# -----------------------------
def test_csv_writes_mismatch(sample_files):
    fileA, fileB, output_dir = sample_files
    mismatched = [("file.txt", fileA, [(fileB, 100, 1234567890.0)])]
    write_csv_output(output_dir, [], mismatched, [])
    rows = read_csv(os.path.join(output_dir, "comparison.csv"))
    assert len(rows) == 2  # header + 1 mismatch
    assert rows[1][0] == "Mismatch"

def test_csv_writes_multiple_mismatch_candidates(sample_files):
    fileA, fileB, output_dir = sample_files
    mismatched = [("file.txt", fileA, [
        (fileB, 100, 1234567890.0),
        (fileB, 200, 1234567891.0),
    ])]
    write_csv_output(output_dir, [], mismatched, [])
    rows = read_csv(os.path.join(output_dir, "comparison.csv"))
    assert len(rows) == 3  # header + 2 mismatch rows

def test_csv_skips_mismatch_with_invalid_pathA(tmp_path):
    fileB = tmp_path / "fileB.txt"
    fileB.write_text("content")
    mismatched = [("file.txt", "fake/path.txt", [(str(fileB), 100, 0)])]
    write_csv_output(str(tmp_path), [], mismatched, [])
    rows = read_csv(str(tmp_path / "comparison.csv"))
    assert len(rows) == 1  # only header

def test_csv_skips_mismatch_with_invalid_pathB(tmp_path):
    fileA = tmp_path / "fileA.txt"
    fileA.write_text("content")
    mismatched = [("file.txt", str(fileA), [("fake/pathB.txt", 100, 0)])]
    write_csv_output(str(tmp_path), [], mismatched, [])
    rows = read_csv(str(tmp_path / "comparison.csv"))
    assert len(rows) == 1  # only header

# -----------------------------
# Missing tests
# -----------------------------
def test_csv_writes_missing(sample_files):
    fileA, fileB, output_dir = sample_files
    missing = [("file.txt", fileA)]
    write_csv_output(output_dir, [], [], missing)
    rows = read_csv(os.path.join(output_dir, "comparison.csv"))
    assert len(rows) == 2  # header + 1 missing
    assert rows[1][0] == "Missing in Folder B"

def test_csv_skips_missing_with_invalid_pathA(tmp_path):
    missing = [("file.txt", "fake/path.txt")]
    write_csv_output(str(tmp_path), [], [], missing)
    rows = read_csv(str(tmp_path / "comparison.csv"))
    assert len(rows) == 1  # only header

def test_csv_missing_has_empty_pathB_columns(sample_files):
    fileA, fileB, output_dir = sample_files
    missing = [("file.txt", fileA)]
    write_csv_output(output_dir, [], [], missing)
    rows = read_csv(os.path.join(output_dir, "comparison.csv"))
    assert rows[1][4] == ""  # Path B empty
    assert rows[1][5] == ""  # Timestamp B empty

# -----------------------------
# Callback tests
# -----------------------------
def test_csv_status_callback_called(tmp_path):
    from unittest.mock import MagicMock
    status_mock = MagicMock()
    write_csv_output(str(tmp_path), [], [], [], status_callback=status_mock)
    assert status_mock.called

def test_csv_progress_callback_called(tmp_path):
    from unittest.mock import MagicMock
    progress_mock = MagicMock()
    write_csv_output(str(tmp_path), [], [], [], progress_callback=progress_mock)
    progress_mock.assert_called_with(75)

# -----------------------------
# Combined data test
# -----------------------------
def test_csv_writes_all_types(sample_files):
    fileA, fileB, output_dir = sample_files
    matches   = [("match.txt", fileA, fileB)]
    mismatched = [("mismatch.txt", fileA, [(fileB, 100, 0)])]
    missing   = [("missing.txt", fileA)]
    write_csv_output(output_dir, matches, mismatched, missing)
    rows = read_csv(os.path.join(output_dir, "comparison.csv"))
    statuses = [r[0] for r in rows[1:]]
    assert "Exact Match" in statuses
    assert "Mismatch" in statuses
    assert "Missing in Folder B" in statuses

    # -----------------------------
    # Timestamp exception handling tests
    # -----------------------------


def test_csv_match_handles_timestamp_error(tmp_path, monkeypatch):
    """Should write empty timestamp if getmtime fails on pathA or pathB."""
    fileA = tmp_path / "fileA.txt"
    fileB = tmp_path / "fileB.txt"
    fileA.write_text("content")
    fileB.write_text("content")

    def fake_getmtime(path):
            raise OSError("Permission denied")

    monkeypatch.setattr(os.path, "getmtime", fake_getmtime)

    matches = [("file.txt", str(fileA), str(fileB))]
    write_csv_output(str(tmp_path), matches, [], [])
    rows = read_csv(str(tmp_path / "comparison.csv"))

    assert len(rows) == 2
    assert rows[1][3] == ""  # tsA empty
    assert rows[1][5] == ""  # tsB empty


def test_csv_mismatch_handles_timestamp_error(tmp_path, monkeypatch):
    """Should write empty timestamp if getmtime fails on mismatch paths."""
    fileA = tmp_path / "fileA.txt"
    fileB = tmp_path / "fileB.txt"
    fileA.write_text("content")
    fileB.write_text("content")

    def fake_getmtime(path):
        raise OSError("Permission denied")

    monkeypatch.setattr(os.path, "getmtime", fake_getmtime)

    mismatched = [("file.txt", str(fileA), [(str(fileB), 100, 0)])]
    write_csv_output(str(tmp_path), [], mismatched, [])
    rows = read_csv(str(tmp_path / "comparison.csv"))

    assert len(rows) == 2
    assert rows[1][3] == ""  # tsA empty
    assert rows[1][5] == ""  # tsB empty


def test_csv_missing_handles_timestamp_error(tmp_path, monkeypatch):
    """Should write empty timestamp if getmtime fails on missing path."""
    fileA = tmp_path / "fileA.txt"
    fileA.write_text("content")

    def fake_getmtime(path):
        raise OSError("Permission denied")

    monkeypatch.setattr(os.path, "getmtime", fake_getmtime)

    missing = [("file.txt", str(fileA))]
    write_csv_output(str(tmp_path), [], [], missing)
    rows = read_csv(str(tmp_path / "comparison.csv"))

    assert len(rows) == 2
    assert rows[1][3] == ""  # tsA empty


def test_csv_handles_write_error(tmp_path, monkeypatch):
    """Should handle file write errors gracefully."""

    def fake_open(*args, **kwargs):
        raise PermissionError("Cannot write file")

    monkeypatch.setattr("builtins.open", fake_open)

    # Should not raise
    write_csv_output(str(tmp_path), [], [], [])
