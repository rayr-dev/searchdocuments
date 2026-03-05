# tests/test_scan_folder.py
# System
import os
import logging

# local
import config
from src.utilities.scan_folder import scan_folder, dump_scan_results

# -----------------------------
# scan_folder - single match mode (multi=False)
# -----------------------------
def test_scan_folder_returns_dict(tmp_path):
    (tmp_path / "file1.txt").write_text("hello")
    result = scan_folder(str(tmp_path))
    assert isinstance(result, dict)

def test_scan_folder_finds_file(tmp_path):
    (tmp_path / "file1.txt").write_text("hello")
    result = scan_folder(str(tmp_path))
    assert "file1.txt" in result

def test_scan_folder_finds_multiple_files(tmp_path):
    (tmp_path / "file1.txt").write_text("hello")
    (tmp_path / "file2.txt").write_text("world")
    result = scan_folder(str(tmp_path))
    assert "file1.txt" in result
    assert "file2.txt" in result

def test_scan_folder_single_mode_value_is_tuple(tmp_path):
    (tmp_path / "file1.txt").write_text("hello")
    result = scan_folder(str(tmp_path))
    value = result["file1.txt"]
    # Should be (full_path, size, mtime)
    assert isinstance(value, tuple)
    assert len(value) == 3

def test_scan_folder_single_mode_path_is_absolute(tmp_path):
    (tmp_path / "file1.txt").write_text("hello")
    result = scan_folder(str(tmp_path))
    full_path, size, mtime = result["file1.txt"]
    assert os.path.isabs(full_path)

def test_scan_folder_single_mode_size_is_correct(tmp_path):
    test_file = tmp_path / "file1.txt"
    test_file.write_text("hello")
    result = scan_folder(str(tmp_path))
    full_path, size, mtime = result["file1.txt"]
    assert size == os.path.getsize(str(test_file))

def test_scan_folder_single_mode_last_file_wins(tmp_path):
    # In single mode, if two files share a name in subfolders
    # the last one scanned wins
    sub1 = tmp_path / "sub1"
    sub1.mkdir()
    (sub1 / "file.txt").write_text("version1")
    result = scan_folder(str(tmp_path))
    assert "file.txt" in result

def test_scan_folder_empty_folder_returns_empty_dict(tmp_path):
    result = scan_folder(str(tmp_path))
    assert result == {}

def test_scan_folder_scans_subfolders(tmp_path):
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "nested.txt").write_text("nested content")
    result = scan_folder(str(tmp_path))
    assert "nested.txt" in result

# -----------------------------
# scan_folder - multi match mode (multi=True)
# -----------------------------
def test_scan_folder_multi_mode_returns_list(tmp_path):
    (tmp_path / "file1.txt").write_text("hello")
    result = scan_folder(str(tmp_path), multi=True)
    assert isinstance(result["file1.txt"], list)

def test_scan_folder_multi_mode_list_contains_tuples(tmp_path):
    (tmp_path / "file1.txt").write_text("hello")
    result = scan_folder(str(tmp_path), multi=True)
    for entry in result["file1.txt"]:
        assert isinstance(entry, tuple)
        assert len(entry) == 3

def test_scan_folder_multi_mode_finds_duplicates(tmp_path):
    # Same filename in two subfolders should both appear in multi mode
    sub1 = tmp_path / "sub1"
    sub2 = tmp_path / "sub2"
    sub1.mkdir()
    sub2.mkdir()
    (sub1 / "file.txt").write_text("version1")
    (sub2 / "file.txt").write_text("version2")
    result = scan_folder(str(tmp_path), multi=True)
    assert len(result["file.txt"]) == 2

def test_scan_folder_multi_mode_empty_folder(tmp_path):
    result = scan_folder(str(tmp_path), multi=True)
    assert result == {}

# -----------------------------
# dump_scan_results tests
# -----------------------------
def test_dump_scan_results_runs_without_error(tmp_path, caplog):
    import config
    # capsys is a pytest built-in that captures print output
    config.DIAGNOSTIC_MODE = True
    filesA = {"file1.txt": (str(tmp_path / "file1.txt"), 100, 1000.0)}
    filesB = {"file1.txt": [(str(tmp_path / "file1.txt"), 100, 1000.0)]}
    with caplog.at_level(logging.DEBUG):
        dump_scan_results(filesA, filesB)
    assert "FILES A" in caplog.text
    assert "FILES B" in caplog.text
    config.DIAGNOSTIC_MODE = False

def test_dump_scan_results_shows_keys(tmp_path, caplog):
    import config
    config.DIAGNOSTIC_MODE = True
    filesA = {"myfile.txt": (str(tmp_path / "myfile.txt"), 200, 2000.0)}
    filesB = {}
    with caplog.at_level(logging.DEBUG):
        dump_scan_results(filesA, filesB)
    assert "myfile.txt" in caplog.text
    assert "myfile.txt" in caplog.text
    config.DIAGNOSTIC_MODE = False

def test_scan_folder_skips_unreadable_file(tmp_path, monkeypatch):
    (tmp_path / "locked.txt").write_text("data")

    # monkeypatch tricks os.path.getsize into raising an error
    def fake_getsize(path):
        raise PermissionError("Access denied")

    monkeypatch.setattr(os.path, "getsize", fake_getsize)

    result = scan_folder(str(tmp_path))
    assert result == {}  # file was skipped, nothing returned