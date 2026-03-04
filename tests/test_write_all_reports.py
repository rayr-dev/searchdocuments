# tests/test_write_all_reports.py

import os
import pytest
from unittest.mock import MagicMock, patch
from src.writers.write_all_reports import write_all_reports

# Patch targets
PATCH_EXCEL   = "src.writers.write_all_reports.write_excel_output"
PATCH_CSV     = "src.writers.write_all_reports.write_csv_output"
PATCH_TEXT    = "src.writers.write_all_reports.write_text_output"
PATCH_SUMMARY = "src.writers.write_all_reports.build_summary"

# -----------------------------
# Helper: patch all writers
# -----------------------------
def all_writer_patches():
    return [
        patch(PATCH_EXCEL,   return_value=None),
        patch(PATCH_CSV,     return_value=None),
        patch(PATCH_TEXT,    return_value=None),
        patch(PATCH_SUMMARY, return_value=None),
    ]

# -----------------------------
# Basic tests
# -----------------------------
def test_write_all_creates_output_dir(tmp_path):
    new_dir = str(tmp_path / "new_output")
    with patch(PATCH_EXCEL,   return_value=None), \
         patch(PATCH_CSV,     return_value=None), \
         patch(PATCH_TEXT,    return_value=None), \
         patch(PATCH_SUMMARY, return_value=None):
        write_all_reports(new_dir, [], [], [])
    assert os.path.isdir(new_dir)

def test_write_all_calls_excel_writer(tmp_path):
    with patch(PATCH_EXCEL,   return_value=None) as mock_excel, \
         patch(PATCH_CSV,     return_value=None), \
         patch(PATCH_TEXT,    return_value=None), \
         patch(PATCH_SUMMARY, return_value=None):
        write_all_reports(str(tmp_path), [], [], [])
    assert mock_excel.called

def test_write_all_calls_csv_writer(tmp_path):
    with patch(PATCH_EXCEL,   return_value=None), \
         patch(PATCH_CSV,     return_value=None) as mock_csv, \
         patch(PATCH_TEXT,    return_value=None), \
         patch(PATCH_SUMMARY, return_value=None):
        write_all_reports(str(tmp_path), [], [], [])
    assert mock_csv.called

def test_write_all_calls_text_writer(tmp_path):
    with patch(PATCH_EXCEL,   return_value=None), \
         patch(PATCH_CSV,     return_value=None), \
         patch(PATCH_TEXT,    return_value=None) as mock_text, \
         patch(PATCH_SUMMARY, return_value=None):
        write_all_reports(str(tmp_path), [], [], [])
    assert mock_text.called

def test_write_all_calls_summary_writer(tmp_path):
    with patch(PATCH_EXCEL,   return_value=None), \
         patch(PATCH_CSV,     return_value=None), \
         patch(PATCH_TEXT,    return_value=None), \
         patch(PATCH_SUMMARY, return_value=None) as mock_summary:
        write_all_reports(str(tmp_path), [], [], [])
    assert mock_summary.called

# -----------------------------
# Callback tests
# -----------------------------
def test_write_all_status_callback_called(tmp_path):
    status_mock = MagicMock()
    with patch(PATCH_EXCEL,   return_value=None), \
         patch(PATCH_CSV,     return_value=None), \
         patch(PATCH_TEXT,    return_value=None), \
         patch(PATCH_SUMMARY, return_value=None):
        write_all_reports(str(tmp_path), [], [], [], status_callback=status_mock)
    assert status_mock.called

def test_write_all_status_callback_final_message(tmp_path):
    status_mock = MagicMock()
    with patch(PATCH_EXCEL,   return_value=None), \
         patch(PATCH_CSV,     return_value=None), \
         patch(PATCH_TEXT,    return_value=None), \
         patch(PATCH_SUMMARY, return_value=None):
        write_all_reports(str(tmp_path), [], [], [], status_callback=status_mock)
    # Last call should mention reports written
    last_call = status_mock.call_args_list[-1][0][0]
    assert "Reports written to" in last_call

def test_write_all_progress_callback_passed(tmp_path):
    progress_mock = MagicMock()
    with patch(PATCH_EXCEL,   return_value=None) as mock_excel, \
         patch(PATCH_CSV,     return_value=None), \
         patch(PATCH_TEXT,    return_value=None), \
         patch(PATCH_SUMMARY, return_value=None):
        write_all_reports(str(tmp_path), [], [], [],
                         progress_callback=progress_mock)
        _, kwargs = mock_excel.call_args
        assert kwargs["progress_callback"] == progress_mock

# -----------------------------
# Error isolation tests
# -----------------------------
def test_excel_failure_does_not_stop_csv(tmp_path):
    """If Excel writer fails CSV should still run."""
    with patch(PATCH_EXCEL,   side_effect=Exception("Excel failed")), \
         patch(PATCH_CSV,     return_value=None) as mock_csv, \
         patch(PATCH_TEXT,    return_value=None), \
         patch(PATCH_SUMMARY, return_value=None):
        write_all_reports(str(tmp_path), [], [], [])
    assert mock_csv.called

def test_csv_failure_does_not_stop_text(tmp_path):
    """If CSV writer fails Text should still run."""
    with patch(PATCH_EXCEL,   return_value=None), \
         patch(PATCH_CSV,     side_effect=Exception("CSV failed")), \
         patch(PATCH_TEXT,    return_value=None) as mock_text, \
         patch(PATCH_SUMMARY, return_value=None):
        write_all_reports(str(tmp_path), [], [], [])
    assert mock_text.called

def test_text_failure_does_not_stop_summary(tmp_path):
    """If Text writer fails Summary should still run."""
    with patch(PATCH_EXCEL,   return_value=None), \
         patch(PATCH_CSV,     return_value=None), \
         patch(PATCH_TEXT,    side_effect=Exception("Text failed")), \
         patch(PATCH_SUMMARY, return_value=None) as mock_summary:
        write_all_reports(str(tmp_path), [], [], [])
    assert mock_summary.called

def test_excel_failure_reports_status(tmp_path):
    """Excel failure should report error via status callback."""
    status_mock = MagicMock()
    with patch(PATCH_EXCEL,   side_effect=Exception("Excel failed")), \
         patch(PATCH_CSV,     return_value=None), \
         patch(PATCH_TEXT,    return_value=None), \
         patch(PATCH_SUMMARY, return_value=None):
        write_all_reports(str(tmp_path), [], [], [],
                         status_callback=status_mock)
    calls = [c[0][0] for c in status_mock.call_args_list]
    assert any("ERROR" in c for c in calls)

def test_csv_failure_reports_status(tmp_path):
    """CSV failure should report error via status callback."""
    status_mock = MagicMock()
    with patch(PATCH_EXCEL,   return_value=None), \
         patch(PATCH_CSV,     side_effect=Exception("CSV failed")), \
         patch(PATCH_TEXT,    return_value=None), \
         patch(PATCH_SUMMARY, return_value=None):
        write_all_reports(str(tmp_path), [], [], [],
                         status_callback=status_mock)
    calls = [c[0][0] for c in status_mock.call_args_list]
    assert any("ERROR" in c for c in calls)

def test_text_failure_reports_status(tmp_path):
    """Text failure should report error via status callback."""
    status_mock = MagicMock()
    with patch(PATCH_EXCEL,   return_value=None), \
         patch(PATCH_CSV,     return_value=None), \
         patch(PATCH_TEXT,    side_effect=Exception("Text failed")), \
         patch(PATCH_SUMMARY, return_value=None):
        write_all_reports(str(tmp_path), [], [], [],
                         status_callback=status_mock)
    calls = [c[0][0] for c in status_mock.call_args_list]
    assert any("ERROR" in c for c in calls)

# -----------------------------
# Output dir creation failure
# -----------------------------
def test_returns_early_if_output_dir_cannot_be_created(tmp_path, monkeypatch):
    """If output dir creation fails should return early."""
    def fake_makedirs(path, exist_ok=False):
        raise PermissionError("Cannot create dir")
    monkeypatch.setattr(os, "makedirs", fake_makedirs)

    with patch(PATCH_EXCEL,   return_value=None) as mock_excel, \
         patch(PATCH_CSV,     return_value=None), \
         patch(PATCH_TEXT,    return_value=None), \
         patch(PATCH_SUMMARY, return_value=None):
        write_all_reports(str(tmp_path / "blocked"), [], [], [])

    # No writers should be called if dir creation fails
    assert not mock_excel.called

def test_output_dir_failure_reports_status(tmp_path, monkeypatch):
    """If output dir creation fails status callback should report error."""
    def fake_makedirs(path, exist_ok=False):
        raise PermissionError("Cannot create dir")
    monkeypatch.setattr(os, "makedirs", fake_makedirs)

    status_mock = MagicMock()
    with patch(PATCH_EXCEL,   return_value=None), \
         patch(PATCH_CSV,     return_value=None), \
         patch(PATCH_TEXT,    return_value=None), \
         patch(PATCH_SUMMARY, return_value=None):
        write_all_reports(str(tmp_path / "blocked"), [], [], [],
                         status_callback=status_mock)
    calls = [c[0][0] for c in status_mock.call_args_list]
    assert any("ERROR" in c for c in calls)

def test_summary_failure_does_not_stop_final_status(tmp_path):
    """If Summary writer fails final status should still be reported."""
    status_mock = MagicMock()
    with patch(PATCH_EXCEL,   return_value=None), \
         patch(PATCH_CSV,     return_value=None), \
         patch(PATCH_TEXT,    return_value=None), \
         patch(PATCH_SUMMARY, side_effect=Exception("Summary failed")):
        write_all_reports(str(tmp_path), [], [], [],
                         status_callback=status_mock)
    calls = [c[0][0] for c in status_mock.call_args_list]
    assert any("Reports written to" in c for c in calls)

def test_summary_failure_reports_status(tmp_path):
    """Summary failure should report error via status callback."""
    status_mock = MagicMock()
    with patch(PATCH_EXCEL,   return_value=None), \
         patch(PATCH_CSV,     return_value=None), \
         patch(PATCH_TEXT,    return_value=None), \
         patch(PATCH_SUMMARY, side_effect=Exception("Summary failed")):
        write_all_reports(str(tmp_path), [], [], [],
                         status_callback=status_mock)
    calls = [c[0][0] for c in status_mock.call_args_list]
    assert any("Error writing Summary" in c for c in calls)