# tests/test_summary_writer.py

import os
import pytest
from unittest.mock import MagicMock
from src.writers.summary_writer import build_summary, print_summary

# -----------------------------
# Helper
# -----------------------------
def read_txt(path):
    with open(path, encoding="utf-8") as f:
        return f.read()

# -----------------------------
# print_summary tests
# -----------------------------
def test_print_summary_returns_string():
    result = print_summary([], [], [])
    assert isinstance(result, str)

def test_print_summary_contains_headers():
    result = print_summary([], [], [])
    assert "SUMMARY REPORT" in result

def test_print_summary_shows_zero_counts():
    result = print_summary([], [], [])
    assert "Total Exact Matches:     0" in result
    assert "Total Mismatches:        0" in result
    assert "Total Missing Files:     0" in result

def test_print_summary_counts_matches():
    matches = [
        ("file1.txt", "pathA", "pathB"),
        ("file2.txt", "pathA", "pathB"),
    ]
    result = print_summary(matches, [], [])
    assert "Total Exact Matches:     2" in result

def test_print_summary_counts_mismatches():
    mismatched = [("file1.txt", "pathA", [])]
    result = print_summary([], mismatched, [])
    assert "Total Mismatches:        1" in result

def test_print_summary_counts_missing():
    missing = [("file1.txt", "pathA"), ("file2.txt", "pathA")]
    result = print_summary([], [], missing)
    assert "Total Missing Files:     2" in result

def test_print_summary_detects_multi_match():
    # Same filename appearing twice in matches = multi match
    matches = [
        ("file.txt", "pathA1", "pathB1"),
        ("file.txt", "pathA1", "pathB2"),
    ]
    result = print_summary(matches, [], [])
    assert "Multi-Match Cases:       1" in result

def test_print_summary_no_multi_match_when_unique():
    matches = [
        ("file1.txt", "pathA", "pathB"),
        ("file2.txt", "pathA", "pathB"),
    ]
    result = print_summary(matches, [], [])
    assert "Multi-Match Cases:       0" in result

def test_print_summary_detects_mixed_case():
    # File appears in both matches and mismatched = mixed case
    matches = [("file.txt", "pathA", "pathB1")]
    mismatched = [("file.txt", "pathA", [("pathB2", 100, 0)])]
    result = print_summary(matches, mismatched, [])
    assert "Mixed Match/Mismatch:    1" in result

def test_print_summary_no_mixed_case_when_clean():
    matches = [("file1.txt", "pathA", "pathB")]
    mismatched = [("file2.txt", "pathA", [])]
    result = print_summary(matches, mismatched, [])
    assert "Mixed Match/Mismatch:    0" in result

def test_print_summary_status_callback_not_used():
    # print_summary accepts status_callback but doesn't call it
    status_mock = MagicMock()
    result = print_summary([], [], [], status_callback=status_mock)
    assert isinstance(result, str)

# -----------------------------
# build_summary tests
# -----------------------------
def test_build_summary_creates_file(tmp_path):
    build_summary(str(tmp_path), [], [], [])
    assert os.path.exists(str(tmp_path / "summary.txt"))

def test_build_summary_file_contains_headers(tmp_path):
    build_summary(str(tmp_path), [], [], [])
    content = read_txt(str(tmp_path / "summary.txt"))
    assert "SUMMARY REPORT" in content

def test_build_summary_shows_correct_counts(tmp_path):
    matches   = [("file1.txt", "pathA", "pathB")]
    mismatched = [("file2.txt", "pathA", [])]
    missing   = [("file3.txt", "pathA"), ("file4.txt", "pathA")]
    build_summary(str(tmp_path), matches, mismatched, missing)
    content = read_txt(str(tmp_path / "summary.txt"))
    assert "Total Exact Matches:     1" in content
    assert "Total Mismatches:        1" in content
    assert "Total Missing Files:     2" in content

def test_build_summary_status_callback_called(tmp_path):
    status_mock = MagicMock()
    build_summary(str(tmp_path), [], [], [], status_callback=status_mock)
    assert status_mock.call_count == 2  # called at start and end

def test_build_summary_progress_callback_called(tmp_path):
    progress_mock = MagicMock()
    build_summary(str(tmp_path), [], [], [], progress_callback=progress_mock)
    progress_mock.assert_called_with(95)

def test_build_summary_detects_multi_match(tmp_path):
    matches = [
        ("file.txt", "pathA", "pathB1"),
        ("file.txt", "pathA", "pathB2"),
    ]
    build_summary(str(tmp_path), matches, [], [])
    content = read_txt(str(tmp_path / "summary.txt"))
    assert "Multi-Match Cases:       1" in content

def test_build_summary_detects_mixed_case(tmp_path):
    matches   = [("file.txt", "pathA", "pathB1")]
    mismatched = [("file.txt", "pathA", [("pathB2", 100, 0)])]
    build_summary(str(tmp_path), matches, mismatched, [])
    content = read_txt(str(tmp_path / "summary.txt"))
    assert "Mixed Match/Mismatch:    1" in content

def test_build_summary_content_matches_print_summary(tmp_path):
    """build_summary file content should match print_summary output."""
    matches   = [("file1.txt", "pathA", "pathB")]
    mismatched = [("file2.txt", "pathA", [])]
    missing   = [("file3.txt", "pathA")]

    build_summary(str(tmp_path), matches, mismatched, missing)
    file_content = read_txt(str(tmp_path / "summary.txt"))
    summary_text = print_summary(matches, mismatched, missing)

    assert file_content == summary_text
