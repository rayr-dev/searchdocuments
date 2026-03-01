# tests/test_safe_delete.py

import os
import pytest
from unittest.mock import patch
from src.utilities.safe_delete import safe_delete, move_to_quarantine, handle_delete



def test_safe_delete_dry_run_does_not_delete(tmp_path, monkeypatch):
    """DRY_RUN=True should not delete the file."""
    import src.utilities.safe_delete as safe_delete_mod
    monkeypatch.setattr(safe_delete_mod.config, "DRY_RUN", True)

    test_file = tmp_path / "file.txt"
    test_file.write_text("delete me")

    safe_delete(str(test_file))

    assert test_file.exists()

def test_safe_delete_actually_deletes(tmp_path, monkeypatch):
    """DRY_RUN=False should delete the file."""
    import src.utilities.safe_delete as safe_delete_mod
    monkeypatch.setattr(safe_delete_mod.config, "DRY_RUN", False)

    test_file = tmp_path / "file.txt"
    test_file.write_text("delete me")

    safe_delete(str(test_file))

    assert not test_file.exists()

def test_safe_delete_handles_missing_file(tmp_path, monkeypatch):
    """Should not raise an error if file doesn't exist."""
    import src.utilities.safe_delete as safe_delete_mod
    monkeypatch.setattr(safe_delete_mod.config, "DRY_RUN", False)

    safe_delete(str(tmp_path / "nonexistent.txt"))

def test_safe_delete_handles_permission_error(tmp_path, monkeypatch):
    """Should handle permission errors gracefully."""
    import src.utilities.safe_delete as safe_delete_mod
    monkeypatch.setattr(safe_delete_mod.config, "DRY_RUN", False)

    test_file = tmp_path / "locked.txt"
    test_file.write_text("locked")

    def fake_remove(path):
        raise PermissionError("Access denied")

    monkeypatch.setattr(os, "remove", fake_remove)
    safe_delete(str(test_file))

def test_move_to_quarantine_dry_run(tmp_path, monkeypatch):
    """DRY_RUN=True should not move the file."""
    import src.utilities.safe_delete as safe_delete_mod
    monkeypatch.setattr(safe_delete_mod.config, "DRY_RUN", True)

    test_file = tmp_path / "file.txt"
    test_file.write_text("quarantine me")
    quarantine_dir = str(tmp_path / "quarantine")

    move_to_quarantine(str(test_file), quarantine_dir)

    assert test_file.exists()
    assert not os.path.exists(quarantine_dir)

def test_move_to_quarantine_moves_file(tmp_path, monkeypatch):
    """DRY_RUN=False should move file to quarantine folder."""
    import src.utilities.safe_delete as safe_delete_mod
    monkeypatch.setattr(safe_delete_mod.config, "DRY_RUN", False)

    test_file = tmp_path / "file.txt"
    test_file.write_text("quarantine me")
    quarantine_dir = str(tmp_path / "quarantine")

    move_to_quarantine(str(test_file), quarantine_dir)

    assert not test_file.exists()
    assert os.path.exists(os.path.join(quarantine_dir, "file.txt"))

def test_move_to_quarantine_creates_quarantine_dir(tmp_path, monkeypatch):
    """Quarantine directory should be created if it doesn't exist."""
    import src.utilities.safe_delete as safe_delete_mod
    monkeypatch.setattr(safe_delete_mod.config, "DRY_RUN", False)

    test_file = tmp_path / "file.txt"
    test_file.write_text("quarantine me")
    quarantine_dir = str(tmp_path / "new_quarantine_folder")

    assert not os.path.exists(quarantine_dir)
    move_to_quarantine(str(test_file), quarantine_dir)
    assert os.path.exists(quarantine_dir)

def test_move_to_quarantine_handles_error(tmp_path, monkeypatch):
    """Should handle move errors gracefully."""
    import src.utilities.safe_delete as safe_delete_mod
    import shutil
    monkeypatch.setattr(safe_delete_mod.config, "DRY_RUN", False)

    test_file = tmp_path / "file.txt"
    test_file.write_text("quarantine me")

    def fake_move(src, dst):
        raise PermissionError("Access denied")

    monkeypatch.setattr(shutil, "move", fake_move)
    move_to_quarantine(str(test_file), str(tmp_path / "quarantine"))

def test_handle_delete_uses_quarantine_when_configured(tmp_path, monkeypatch):
    """USE_QUARANTINE=True should call move_to_quarantine."""
    import src.utilities.safe_delete as safe_delete_mod
    monkeypatch.setattr(safe_delete_mod.config, "DRY_RUN", False)
    monkeypatch.setattr(safe_delete_mod.config, "USE_QUARANTINE", True)

    test_file = tmp_path / "file.txt"
    test_file.write_text("handle me")
    quarantine_dir = str(tmp_path / "quarantine")

    handle_delete(str(test_file), quarantine_dir)

    assert not test_file.exists()
    assert os.path.exists(os.path.join(quarantine_dir, "file.txt"))

def test_handle_delete_uses_safe_delete_when_no_quarantine(tmp_path, monkeypatch):
    """USE_QUARANTINE=False should call safe_delete."""
    import src.utilities.safe_delete as safe_delete_mod
    monkeypatch.setattr(safe_delete_mod.config, "DRY_RUN", False)
    monkeypatch.setattr(safe_delete_mod.config, "USE_QUARANTINE", False)

    test_file = tmp_path / "file.txt"
    test_file.write_text("handle me")

    handle_delete(str(test_file))

    assert not test_file.exists()

def test_handle_delete_uses_safe_delete_when_no_quarantine_dir(tmp_path, monkeypatch):
    """USE_QUARANTINE=True but no quarantine_dir falls back to safe_delete."""
    import src.utilities.safe_delete as safe_delete_mod
    monkeypatch.setattr(safe_delete_mod.config, "DRY_RUN", False)
    monkeypatch.setattr(safe_delete_mod.config, "USE_QUARANTINE", True)

    test_file = tmp_path / "file.txt"
    test_file.write_text("handle me")

    handle_delete(str(test_file), quarantine_dir=None)

    assert not test_file.exists()

# -----------------------------
# is_delete_candidate tests
# -----------------------------
def test_is_delete_candidate_same_size_different_timestamp():
    from src.utilities.safe_delete import is_delete_candidate
    from types import SimpleNamespace

    fileA = SimpleNamespace(size=100, timestamp=1000)
    fileB = SimpleNamespace(size=100, timestamp=2000)

    assert is_delete_candidate(fileA, fileB) is True

def test_is_delete_candidate_different_size():
    from src.utilities.safe_delete import is_delete_candidate
    from types import SimpleNamespace

    fileA = SimpleNamespace(size=100, timestamp=1000)
    fileB = SimpleNamespace(size=200, timestamp=1000)

    assert is_delete_candidate(fileA, fileB) is False

def test_is_delete_candidate_same_size_same_timestamp():
    from src.utilities.safe_delete import is_delete_candidate
    from types import SimpleNamespace

    fileA = SimpleNamespace(size=100, timestamp=1000)
    fileB = SimpleNamespace(size=100, timestamp=1000)

    assert is_delete_candidate(fileA, fileB) is False