# tests/test_orchestrator.py

import os
import pytest
from unittest.mock import MagicMock, patch
from src.orchestrator import run_reconciliation

# -----------------------------
# Basic placeholder test
# -----------------------------
def test_basic_example():
    assert 1 + 1 == 2

# -----------------------------
# Input validation tests
# -----------------------------
def test_raises_if_folderA_is_empty():
    with pytest.raises(ValueError, match="Folder A and Folder B must be provided"):
        run_reconciliation("", "some/path", "output/")

def test_raises_if_folderB_is_empty():
    with pytest.raises(ValueError, match="Folder A and Folder B must be provided"):
        run_reconciliation("some/path", "", "output/")

def test_raises_if_both_folders_empty():
    with pytest.raises(ValueError, match="Folder A and Folder B must be provided"):
        run_reconciliation("", "", "output/")

def test_raises_if_folderA_does_not_exist(tmp_path):
    real_folder = str(tmp_path)
    with pytest.raises(ValueError, match="One or both folders are invalid"):
        run_reconciliation("fake/nonexistent/path", real_folder, str(tmp_path))

def test_raises_if_folderB_does_not_exist(tmp_path):
    real_folder = str(tmp_path)
    with pytest.raises(ValueError, match="One or both folders are invalid"):
        run_reconciliation(real_folder, "fake/nonexistent/path", str(tmp_path))

def test_raises_if_both_folders_do_not_exist():
    with pytest.raises(ValueError, match="One or both folders are invalid"):
        run_reconciliation("fake/pathA", "fake/pathB", "output/")

# -----------------------------
# Successful run tests
# (monkeypatches compare_engine so we don't need real files)
# -----------------------------
def test_returns_tuple_on_success(tmp_path):
    folderA = tmp_path / "source"
    folderB = tmp_path / "target"
    output  = tmp_path / "output"
    folderA.mkdir()
    folderB.mkdir()
    output.mkdir()

    mock_results = {"matched": [], "candidates": []}
    mock_summary = "Summary text here"

    with patch("src.orchestrator.compare_folders_recursive",
               return_value=(mock_results, mock_summary)):
        results, summary = run_reconciliation(
            str(folderA), str(folderB), str(output)
        )

    assert isinstance(results, dict)
    assert isinstance(summary, str)

def test_returns_correct_results(tmp_path):
    folderA = tmp_path / "source"
    folderB = tmp_path / "target"
    output  = tmp_path / "output"
    folderA.mkdir()
    folderB.mkdir()
    output.mkdir()

    mock_results = {"matched": ["file1.txt"], "candidates": []}
    mock_summary = "1 match found"

    with patch("src.orchestrator.compare_folders_recursive",
               return_value=(mock_results, mock_summary)):
        results, summary = run_reconciliation(
            str(folderA), str(folderB), str(output)
        )

    assert results == mock_results
    assert summary == "1 match found"

def test_progress_callback_is_passed(tmp_path):
    folderA = tmp_path / "source"
    folderB = tmp_path / "target"
    output  = tmp_path / "output"
    folderA.mkdir()
    folderB.mkdir()
    output.mkdir()

    progress_mock = MagicMock()
    status_mock = MagicMock()

    with patch("src.orchestrator.compare_folders_recursive",
               return_value=({}, "done")) as mock_compare:
        run_reconciliation(
            str(folderA), str(folderB), str(output),
            progress_callback=progress_mock,
            status_callback=status_mock
        )

        # Confirm callbacks were passed through to compare_engine
        _, kwargs = mock_compare.call_args
        assert kwargs["progress_callback"] == progress_mock
        assert kwargs["status_callback"] == status_mock