# tests/test_logging_setup.py

import os
import json
import logging
import pytest
from src.utilities.logging_setup import init_logging, dump_diagnostics, diag

# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging handlers before and after each test to prevent interference."""
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    yield
    for handler in logging.root.handlers[:]:
        handler.close()
        logging.root.removeHandler(handler)

# -----------------------------
# init_logging tests
# -----------------------------
def test_init_logging_creates_log_file(tmp_path):
    log_path = init_logging(str(tmp_path))
    assert os.path.exists(log_path)

def test_init_logging_returns_path(tmp_path):
    log_path = init_logging(str(tmp_path))
    assert isinstance(log_path, str)
    assert log_path.endswith(".log")

def test_init_logging_log_file_in_output_dir(tmp_path):
    log_path = init_logging(str(tmp_path))
    assert str(tmp_path) in log_path

def test_init_logging_filename_contains_timestamp(tmp_path):
    log_path = init_logging(str(tmp_path))
    filename = os.path.basename(log_path)
    assert filename.startswith("reconciliation_")
    assert filename.endswith(".log")

def test_init_logging_creates_output_dir(tmp_path):
    new_dir = str(tmp_path / "new_log_dir")
    assert not os.path.exists(new_dir)
    init_logging(new_dir)
    assert os.path.exists(new_dir)

# -----------------------------
# Fix cwd test - close handlers before cleanup
# -----------------------------
def test_init_logging_defaults_to_cwd_when_no_output_dir():
    """When no output_dir provided should use current working directory."""
    log_path = init_logging()
    assert os.path.exists(log_path)
    assert os.getcwd() in log_path

    # Close handlers before attempting to delete on Windows
    for handler in logging.root.handlers[:]:
        handler.close()
        logging.root.removeHandler(handler)

    if os.path.exists(log_path):
        os.remove(log_path)

# -----------------------------
# Log level tests - read from file instead of caplog
# -----------------------------
def test_init_logging_info_level_by_default(tmp_path):
    log_path = init_logging(str(tmp_path), diagnostic=False)
    logging.info("info message")
    for handler in logging.root.handlers:
        handler.flush()
    content = open(log_path).read()
    assert "info message" in content

def test_init_logging_warning_logged(tmp_path):
    log_path = init_logging(str(tmp_path), diagnostic=False)
    logging.warning("warning message")
    for handler in logging.root.handlers:
        handler.flush()
    content = open(log_path).read()
    assert "warning message" in content

def test_init_logging_error_logged(tmp_path):
    log_path = init_logging(str(tmp_path), diagnostic=False)
    logging.error("error message")
    for handler in logging.root.handlers:
        handler.flush()
    content = open(log_path).read()
    assert "error message" in content

def test_init_logging_critical_logged(tmp_path):
    log_path = init_logging(str(tmp_path), diagnostic=False)
    logging.critical("critical message")
    for handler in logging.root.handlers:
        handler.flush()
    content = open(log_path).read()
    assert "critical message" in content

def test_init_logging_debug_suppressed_when_not_diagnostic(tmp_path):
    """DEBUG messages should NOT appear in log file when diagnostic=False."""
    log_path = init_logging(str(tmp_path), diagnostic=False)
    logging.debug("should be suppressed")
    for handler in logging.root.handlers:
        handler.flush()
    content = open(log_path).read()
    assert "should be suppressed" not in content

def test_init_logging_debug_level_when_diagnostic(tmp_path):
    log_path = init_logging(str(tmp_path), diagnostic=True)
    logging.debug("debug message")
    for handler in logging.root.handlers:
        handler.flush()
    content = open(log_path).read()
    assert "debug message" in content

def test_init_logging_info_appears_in_log_file(tmp_path):
    """INFO messages should appear in log file."""
    log_path = init_logging(str(tmp_path), diagnostic=False)
    logging.info("info to file")

    for handler in logging.root.handlers:
        handler.flush()

    content = open(log_path).read()
    assert "info to file" in content

def test_init_logging_clears_existing_handlers(tmp_path):
    """Calling init_logging twice should not duplicate handlers."""
    init_logging(str(tmp_path))
    handler_count_1 = len(logging.root.handlers)

    init_logging(str(tmp_path))
    handler_count_2 = len(logging.root.handlers)

    assert handler_count_1 == handler_count_2

def test_init_logging_sets_info_level_when_not_diagnostic(tmp_path):
    init_logging(str(tmp_path), diagnostic=False)
    assert logging.root.level == logging.INFO

def test_init_logging_sets_debug_level_when_diagnostic(tmp_path):
    init_logging(str(tmp_path), diagnostic=True)
    assert logging.root.level == logging.DEBUG

# -----------------------------
# diag() function tests
# -----------------------------
def test_diag_logs_at_debug_level(tmp_path):
    log_path = init_logging(str(tmp_path), diagnostic=True)
    diag("test diag message")
    for handler in logging.root.handlers:
        handler.flush()
    content = open(log_path).read()
    assert "test diag message" in content

def test_diag_handles_special_characters(tmp_path):
    log_path = init_logging(str(tmp_path), diagnostic=True)
    diag("special chars: !@#$%^&*()")
    for handler in logging.root.handlers:
        handler.flush()
    content = open(log_path).read()
    assert "special chars" in content

def test_diag_message_appears_in_file_when_diagnostic(tmp_path):
    """diag() output should appear in log file when diagnostic=True."""
    init_logging(str(tmp_path), diagnostic=True)
    diag("diag file message")

    for handler in logging.root.handlers:
        handler.flush()

    log_path = [f for f in os.listdir(str(tmp_path)) if f.endswith(".log")][0]
    content = open(os.path.join(str(tmp_path), log_path)).read()
    assert "diag file message" in content

def test_diag_message_suppressed_when_not_diagnostic(tmp_path):
    """diag() output should NOT appear in log file when diagnostic=False."""
    init_logging(str(tmp_path), diagnostic=False)
    diag("suppressed diag message")

    for handler in logging.root.handlers:
        handler.flush()

    log_path = [f for f in os.listdir(str(tmp_path)) if f.endswith(".log")][0]
    content = open(os.path.join(str(tmp_path), log_path)).read()
    assert "suppressed diag message" not in content

def test_diag_handles_empty_string(tmp_path, caplog):
    init_logging(str(tmp_path), diagnostic=True)
    with caplog.at_level(logging.DEBUG):
        diag("")  # should not raise

# -----------------------------
# dump_diagnostics tests
# -----------------------------
def test_dump_diagnostics_creates_file(tmp_path):
    init_logging(str(tmp_path))
    data = {"matches": [], "mismatched": [], "missing": []}
    path = dump_diagnostics(data, str(tmp_path))
    assert os.path.exists(path)

def test_dump_diagnostics_returns_path(tmp_path):
    init_logging(str(tmp_path))
    data = {"test": "value"}
    path = dump_diagnostics(data, str(tmp_path))
    assert isinstance(path, str)
    assert path.endswith(".json")

def test_dump_diagnostics_default_filename(tmp_path):
    init_logging(str(tmp_path))
    path = dump_diagnostics({}, str(tmp_path))
    assert os.path.basename(path) == "diagnostics_dump.json"

def test_dump_diagnostics_custom_filename(tmp_path):
    init_logging(str(tmp_path))
    path = dump_diagnostics({}, str(tmp_path), filename="custom.json")
    assert os.path.basename(path) == "custom.json"

def test_dump_diagnostics_writes_valid_json(tmp_path):
    init_logging(str(tmp_path))
    data = {"matches": ["file1.txt"], "missing": ["file2.txt"]}
    path = dump_diagnostics(data, str(tmp_path))
    with open(path) as f:
        loaded = json.load(f)
    assert loaded == data

def test_dump_diagnostics_creates_output_dir(tmp_path):
    init_logging(str(tmp_path))
    new_dir = str(tmp_path / "diag_output")
    assert not os.path.exists(new_dir)
    dump_diagnostics({}, new_dir)
    assert os.path.exists(new_dir)

def test_dump_diagnostics_returns_none_on_error(tmp_path, monkeypatch):
    init_logging(str(tmp_path))

    def fake_open(*args, **kwargs):
        raise PermissionError("Cannot write")
    monkeypatch.setattr("builtins.open", fake_open)

    result = dump_diagnostics({"test": "data"}, str(tmp_path))
    assert result is None

def test_dump_diagnostics_logs_success(tmp_path):
    log_path = init_logging(str(tmp_path))
    dump_diagnostics({"test": "value"}, str(tmp_path))
    for handler in logging.root.handlers:
        handler.flush()
    content = open(log_path).read()
    assert "Diagnostic dump written" in content

def test_dump_diagnostics_handles_nested_data(tmp_path):
    init_logging(str(tmp_path))
    data = {
        "matches": [["file.txt", "pathA", "pathB"]],
        "mismatched": [["file2.txt", "pathA", [["pathB", 100, 0]]]],
        "missing": [["file3.txt", "pathA"]]
    }
    path = dump_diagnostics(data, str(tmp_path))
    with open(path) as f:
        loaded = json.load(f)
    assert loaded == data
