# tests/test_compare_engine.py

# System
import os
import pytest
from unittest.mock import patch, MagicMock

# Locals

# -----------------------------
# Shared test fixtures
# -----------------------------
@pytest.fixture
def folders(tmp_path):
    """Create real temporary folders for A, B, and output."""
    folderA = tmp_path / "source"
    folderB = tmp_path / "target"
    output  = tmp_path / "output"
    folderA.mkdir()
    folderB.mkdir()
    output.mkdir()
    return str(folderA), str(folderB), str(output)

def make_call(folderA, folderB, output, **kwargs):
    """Helper to call compare_folders_recursive with safe defaults."""
    from src.engine.compare_engine import compare_folders_recursive
    return compare_folders_recursive(
        folderA, folderB, output,
        return_results=True,
        return_summary=True,
        **kwargs
    )

# Patch targets used repeatedly
PATCH_WRITE    = "src.engine.compare_engine.write_all_reports"
PATCH_SUMMARY  = "src.engine.compare_engine.print_summary"
PATCH_DUMP     = "src.engine.compare_engine.dump_diagnostics"
PATCH_SCANRES  = "src.engine.compare_engine.dump_scan_results"

# -----------------------------
# Helper: build a safe patch context
# -----------------------------
def safe_patches():
    """Returns a list of patches that prevent real file I/O in reports."""
    return [
        patch(PATCH_WRITE,   return_value=None),
        patch(PATCH_SUMMARY, return_value="Mock summary"),
        patch(PATCH_DUMP,    return_value=None),
        patch(PATCH_SCANRES, return_value=None),
    ]

# -----------------------------
# Return type tests
# -----------------------------
def test_returns_tuple(folders):
    folderA, folderB, output = folders
    with patch(PATCH_WRITE, return_value=None), \
         patch(PATCH_SUMMARY, return_value="summary"), \
         patch(PATCH_DUMP, return_value=None), \
         patch(PATCH_SCANRES, return_value=None):
        result = make_call(folderA, folderB, output)
    assert isinstance(result, tuple)
    assert len(result) == 2

def test_returns_results_dict(folders):
    folderA, folderB, output = folders
    with patch(PATCH_WRITE, return_value=None), \
         patch(PATCH_SUMMARY, return_value="summary"), \
         patch(PATCH_DUMP, return_value=None), \
         patch(PATCH_SCANRES, return_value=None):
        results, summary = make_call(folderA, folderB, output)
    assert "matches" in results
    assert "mismatched" in results
    assert "missing" in results
    assert "source_count" in results
    assert "target_count" in results
    assert "source_unique" in results
    assert "target_unique" in results

def test_returns_summary_string(folders):
    folderA, folderB, output = folders
    with patch(PATCH_WRITE, return_value=None), \
         patch(PATCH_SUMMARY, return_value="Mock summary"), \
         patch(PATCH_DUMP, return_value=None), \
         patch(PATCH_SCANRES, return_value=None):
        results, summary = make_call(folderA, folderB, output)
    assert isinstance(summary, str)

# -----------------------------
# Empty folder tests
# -----------------------------
def test_empty_folders_return_empty_results(folders):
    folderA, folderB, output = folders
    with patch(PATCH_WRITE, return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP, return_value=None), \
         patch(PATCH_SCANRES, return_value=None):
        results, _ = make_call(folderA, folderB, output)
    assert results["matches"] == []
    assert results["mismatched"] == []
    assert results["missing"] == []

# -----------------------------
# Timestamp match tests
# -----------------------------
def test_timestamp_match_detected(folders, monkeypatch):
    folderA, folderB, output = folders

    import src.engine.compare_engine as engine_module  # ← patch via engin
    monkeypatch.setattr(engine_module.config, "HASH_ONLY_MODE", False)
    monkeypatch.setattr(engine_module.config, "HASH_COMPARE_MODE", False)
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT", False)

    # Create matching files in both folders
    fileA = (folderA + "/file.txt")
    fileB = (folderB + "/file.txt")
    open(fileA, "w").write("same content")
    open(fileB, "w").write("same content")

    # Force same size and mtime
    import os
    mtime = os.path.getmtime(fileA)
    os.utime(fileB, (mtime, mtime))

    with patch(PATCH_WRITE, return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP, return_value=None), \
         patch(PATCH_SCANRES, return_value=None):
        results, _ = make_call(folderA, folderB, output)

    assert len(results["matches"]) == 1
    assert results["matches"][0][0] == "file.txt"

def test_missing_file_detected(folders, monkeypatch):
    folderA, folderB, output = folders

    import src.engine.compare_engine as engine_module  # ← patch via engin
    monkeypatch.setattr(engine_module.config, "HASH_ONLY_MODE", False)
    monkeypatch.setattr(engine_module.config, "HASH_COMPARE_MODE", False)
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT", False)

    # Only create file in A, not in B
    open(folderA + "/missing.txt", "w").write("only in A")

    with patch(PATCH_WRITE, return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP, return_value=None), \
         patch(PATCH_SCANRES, return_value=None):
        results, _ = make_call(folderA, folderB, output)

    assert len(results["missing"]) == 1
    assert results["missing"][0][0] == "missing.txt"

def test_mismatch_detected(folders, monkeypatch):
    folderA, folderB, output = folders

    import src.engine.compare_engine as engine_module  # ← patch via engine
    monkeypatch.setattr(engine_module.config, "HASH_ONLY_MODE", False)
    monkeypatch.setattr(engine_module.config, "HASH_COMPARE_MODE", False)
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT", False)

    # Same filename, different content and mtime
    open(folderA + "/file.txt", "w").write("version A")
    open(folderB + "/file.txt", "w").write("version B is longer content")

    with patch(PATCH_WRITE, return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP, return_value=None), \
         patch(PATCH_SCANRES, return_value=None):
        results, _ = make_call(folderA, folderB, output)

    assert len(results["mismatched"]) == 1
    assert results["mismatched"][0][0] == "file.txt"

# -----------------------------
# Hash only mode tests
# -----------------------------
def test_hash_only_mode_match(folders, monkeypatch):
    folderA, folderB, output = folders

    import src.engine.compare_engine as engine_module  # ← patch via engine
    monkeypatch.setattr(engine_module.config, "HASH_ONLY_MODE", True)
    monkeypatch.setattr(engine_module.config, "HASH_COMPARE_MODE", False)
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT", False)

    # Same content, different mtime — should still match via hash
    open(folderA + "/file.txt", "w").write("identical content")
    open(folderB + "/file.txt", "w").write("identical content")

    import os
    import time
    time.sleep(0.1)
    os.utime(folderB + "/file.txt", None)  # bump mtime on B

    with patch(PATCH_WRITE, return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP, return_value=None), \
         patch(PATCH_SCANRES, return_value=None):
        results, _ = make_call(folderA, folderB, output)

    assert len(results["matches"]) == 1

# -----------------------------
# Callback tests
# -----------------------------
def test_status_callback_called(folders, monkeypatch):
    folderA, folderB, output = folders

    import src.engine.compare_engine as engine_module  # ← patch via engine
    monkeypatch.setattr(engine_module.config, "HASH_ONLY_MODE", False)
    monkeypatch.setattr(engine_module.config, "HASH_COMPARE_MODE", False)
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT", False)

    status_mock = MagicMock()

    with patch(PATCH_WRITE, return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP, return_value=None), \
         patch(PATCH_SCANRES, return_value=None):
        make_call(folderA, folderB, output, status_callback=status_mock)

    assert status_mock.called
    assert status_mock.call_count >= 2  # at minimum "Scanning" and "Complete"

def test_progress_callback_called(folders, monkeypatch):
    folderA, folderB, output = folders

    import src.engine.compare_engine as engine_module  # ← patch via engine
    monkeypatch.setattr(engine_module.config, "HASH_ONLY_MODE", False)
    monkeypatch.setattr(engine_module.config, "HASH_COMPARE_MODE", False)
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT", False)

    progress_mock = MagicMock()

    with patch(PATCH_WRITE, return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP, return_value=None), \
         patch(PATCH_SCANRES, return_value=None):
        make_call(folderA, folderB, output, progress_callback=progress_mock)

    assert progress_mock.called

# -----------------------------
# Accurate mode (hash confirm) tests
# Lines 73-80
# -----------------------------
def test_accurate_mode_hash_match(folders, monkeypatch):
    """Same size, same content — should match via hash confirm."""
    folderA, folderB, output = folders

    import src.engine.compare_engine as engine_module  # ← patch via engine
    monkeypatch.setattr(engine_module.config, "HASH_ONLY_MODE", False)
    monkeypatch.setattr(engine_module.config, "HASH_COMPARE_MODE", True)
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT", False)
    monkeypatch.setattr(engine_module.config, "FIND_ALL_LOCATIONS_MODE", True)

    # Same content = same size + same hash, but different mtime
    open(folderA + "/file.txt", "w").write("identical content")
    open(folderB + "/file.txt", "w").write("identical content")

    # Force different mtime so timestamp branch is skipped
    import os
    mtime_a = os.path.getmtime(folderA + "/file.txt")
    os.utime(folderB + "/file.txt", (mtime_a + 10, mtime_a + 10))

    with patch(PATCH_WRITE, return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP, return_value=None), \
         patch(PATCH_SCANRES, return_value=None):
        results, _ = make_call(folderA, folderB, output)

    assert len(results["matches"]) == 1

def test_accurate_mode_hash_mismatch(folders, monkeypatch):
    """Same size, different content — hash should not match, goes to mismatch."""
    folderA, folderB, output = folders

    import src.engine.compare_engine as engine_module  # ← patch via engine
    monkeypatch.setattr(engine_module.config, "HASH_ONLY_MODE", False)
    monkeypatch.setattr(engine_module.config, "HASH_COMPARE_MODE", True)
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT", False)

    # Same size but different content
    open(folderA + "/file.txt", "w").write("aaaaaaaaa")
    open(folderB + "/file.txt", "w").write("bbbbbbbbb")

    # Force different mtime so timestamp branch is skipped
    import os
    mtime_a = os.path.getmtime(folderA + "/file.txt")
    os.utime(folderB + "/file.txt", (mtime_a + 10, mtime_a + 10))

    with patch(PATCH_WRITE, return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP, return_value=None), \
         patch(PATCH_SCANRES, return_value=None):
        results, _ = make_call(folderA, folderB, output)

    assert len(results["mismatched"]) == 1

def test_accurate_mode_same_size_diff_timestamp_hash_match(folders, monkeypatch):
    """Same size, different timestamp, same content — should match via hash."""
    folderA, folderB, output = folders

    import src.engine.compare_engine as engine_module  # ← patch via engine
    import os
    monkeypatch.setattr(engine_module.config, "HASH_ONLY_MODE", False)
    monkeypatch.setattr(engine_module.config, "HASH_COMPARE_MODE", True)
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT", False)
    monkeypatch.setattr(engine_module.config, "FIND_ALL_LOCATIONS_MODE", True)

    open(folderA + "/file.txt", "w").write("identical content")
    open(folderB + "/file.txt", "w").write("identical content")

    # Force different mtime AND different size check won't apply
    # but same size — hits lines 133-140
    mtime_a = os.path.getmtime(folderA + "/file.txt")
    os.utime(folderB + "/file.txt", (mtime_a + 100, mtime_a + 100))

    with patch(PATCH_WRITE, return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP, return_value=None), \
         patch(PATCH_SCANRES, return_value=None):
        results, _ = make_call(folderA, folderB, output)

    assert len(results["matches"]) == 1

def test_accurate_mode_same_size_diff_timestamp_hash_mismatch(folders, monkeypatch):
    """Same size, different timestamp, different content — should mismatch."""
    folderA, folderB, output = folders

    import src.engine.compare_engine as engine_module  # ← patch via engine
    import os
    monkeypatch.setattr(engine_module.config, "HASH_ONLY_MODE", False)
    monkeypatch.setattr(engine_module.config, "HASH_COMPARE_MODE", True)
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT", False)
    monkeypatch.setattr(engine_module.config, "FIND_ALL_LOCATIONS_MODE", True)

    # Same size different content
    open(folderA + "/file.txt", "w").write("aaaaaaaaa")
    open(folderB + "/file.txt", "w").write("bbbbbbbbb")

    mtime_a = os.path.getmtime(folderA + "/file.txt")
    os.utime(folderB + "/file.txt", (mtime_a + 100, mtime_a + 100))

    with patch(PATCH_WRITE, return_value=None), \
            patch(PATCH_SUMMARY, return_value=""), \
            patch(PATCH_DUMP, return_value=None), \
            patch(PATCH_SCANRES, return_value=None):
        results, _ = make_call(folderA, folderB, output)

    assert len(results["mismatched"]) == 1

def test_accurate_mode_timestamp_match_rejected_by_hash(folders, monkeypatch):
    """Same size and timestamp but different content — hash rejects the match."""
    folderA, folderB, output = folders

    import src.engine.compare_engine as engine_module  # ← patch via engine
    import os
    monkeypatch.setattr(engine_module.config, "HASH_ONLY_MODE", False)
    monkeypatch.setattr(engine_module.config, "HASH_COMPARE_MODE", True)
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT", False)

    # Same size same timestamp but different content
    open(folderA + "/file.txt", "w").write("aaaaaaaaa")
    open(folderB + "/file.txt", "w").write("bbbbbbbbb")

    # Force same mtime — timestamp check passes but hash should reject
    mtime_a = os.path.getmtime(folderA + "/file.txt")
    os.utime(folderB + "/file.txt", (mtime_a, mtime_a))

    with patch(PATCH_WRITE, return_value=None), \
            patch(PATCH_SUMMARY, return_value=""), \
            patch(PATCH_DUMP, return_value=None), \
            patch(PATCH_SCANRES, return_value=None):
        results, _ = make_call(folderA, folderB, output)

    assert len(results["mismatched"]) == 1

def test_accurate_mode_timestamp_and_hash_match(folders, monkeypatch):
    """Same size, same timestamp, same content — hash confirms match."""
    folderA, folderB, output = folders

    import src.engine.compare_engine as engine_module
    import os
    monkeypatch.setattr(engine_module.config, "HASH_ONLY_MODE", False)
    monkeypatch.setattr(engine_module.config, "HASH_COMPARE_MODE", True)
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT", False)
    monkeypatch.setattr(engine_module.config, "FIND_ALL_LOCATIONS_MODE", True)

    # Same content = same hash
    open(folderA + "/file.txt", "w").write("identical content")
    open(folderB + "/file.txt", "w").write("identical content")

    # Force same mtime so timestamp check passes
    mtime_a = os.path.getmtime(folderA + "/file.txt")
    os.utime(folderB + "/file.txt", (mtime_a, mtime_a))

    with patch(PATCH_WRITE,   return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP,    return_value=None), \
         patch(PATCH_SCANRES, return_value=None):
        results, _ = make_call(folderA, folderB, output)

    assert len(results["matches"]) == 1

# -----------------------------
# Mixed match + mismatch tests
# Lines 84-89, 100
# -----------------------------
def test_mixed_match_and_mismatch(folders, monkeypatch):
    """File matches one copy in B but mismatches another — should appear in both."""
    folderA, folderB, output = folders

    import src.engine.compare_engine as engine_module  # ← patch via engine
    monkeypatch.setattr(engine_module.config, "HASH_ONLY_MODE", False)
    monkeypatch.setattr(engine_module.config, "HASH_COMPARE_MODE", False)
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT", False)

    import os

    # Create file in A
    open(folderA + "/file.txt", "w").write("original")
    mtime_a = os.path.getmtime(folderA + "/file.txt")

    # Create matching copy in B subfolder 1
    sub1 = folderB + "/sub1"
    os.makedirs(sub1)
    open(sub1 + "/file.txt", "w").write("original")
    os.utime(sub1 + "/file.txt", (mtime_a, mtime_a))  # force same mtime

    # Create mismatching copy in B subfolder 2
    sub2 = folderB + "/sub2"
    os.makedirs(sub2)
    open(sub2 + "/file.txt", "w").write("different content here")

    with patch(PATCH_WRITE, return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP, return_value=None), \
         patch(PATCH_SCANRES, return_value=None):
        results, _ = make_call(folderA,
                                folderB,
                                output
                                )

    # Should appear in both matches and mismatched
    assert len(results["matches"]) >= 1
    assert len(results["mismatched"]) >= 1

# -----------------------------
# No match at all — goes to missing
# Line 108
# -----------------------------
def test_no_match_goes_to_missing(folders, monkeypatch):
    """File in A has a candidate in B but nothing matches — goes to missing."""
    folderA, folderB, output = folders

    import src.engine.compare_engine as engine_module  # ← patch via engine
    monkeypatch.setattr(engine_module.config,
                        "HASH_ONLY_MODE",
                        False
                        )
    monkeypatch.setattr(engine_module.config,
                        "HASH_COMPARE_MODE",
                        False
                        )
    monkeypatch.setattr(engine_module.config,
                        "TIMESTAMPED_OUTPUT",
                        False
                        )

    import os

    # File in A
    open(folderA + "/file.txt", "w").write("version A content here")

    # File in B with same name but totally different size and mtime
    open(folderB + "/file.txt", "w").write("x")
    mtime_a = os.path.getmtime(folderA + "/file.txt")
    os.utime(folderB + "/file.txt", (mtime_a + 999, mtime_a + 999))

    with patch(PATCH_WRITE, return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP, return_value=None), \
         patch(PATCH_SCANRES, return_value=None):
        results, _ = make_call(folderA, folderB, output)

    # Should land in mismatched since there was a candidate but no match
    assert len(results["mismatched"]) == 1
    assert results["mismatched"][0][0] == "file.txt"

def test_truly_missing_file_no_candidates(folders, monkeypatch):
    """File in A has NO matching filename in B at all — pure missing."""
    folderA, folderB, output = folders

    import src.engine.compare_engine as engine_module  # ← patch via engine
    monkeypatch.setattr(engine_module.config, "HASH_ONLY_MODE", False)
    monkeypatch.setattr(engine_module.config, "HASH_COMPARE_MODE", False)
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT", False)

    # File in A only — nothing in B with this name
    open(folderA + "/uniquefile.txt", "w").write("only exists in A")
    open(folderB + "/differentname.txt", "w").write("different name entirely")

    with patch(PATCH_WRITE, return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP, return_value=None), \
         patch(PATCH_SCANRES, return_value=None):
        results, _ = make_call(folderA, folderB, output)

    # uniquefile.txt has no candidate in B — should be purely missing
    missing_names = [m[0] for m in results["missing"]]
    assert "uniquefile.txt" in missing_names

def test_found_match_with_mismatch_sibling(folders, monkeypatch):
    """One copy in B matches, another copy in B mismatches — both recorded."""
    folderA, folderB, output = folders

    import src.engine.compare_engine as engine_module  # ← patch via engine
    import os
    monkeypatch.setattr(engine_module.config, "HASH_ONLY_MODE", False)
    monkeypatch.setattr(engine_module.config, "HASH_COMPARE_MODE", False)
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT", False)

    # File in A
    open(folderA + "/report.txt", "w").write("report data")
    mtime_a = os.path.getmtime(folderA + "/report.txt")

    # Matching copy in B/sub1 — same size and mtime
    sub1 = folderB + "/sub1"
    os.makedirs(sub1)
    open(sub1 + "/report.txt", "w").write("report data")
    os.utime(sub1 + "/report.txt", (mtime_a, mtime_a))

    # Mismatching copy in B/sub2 — different size and mtime
    sub2 = folderB + "/sub2"
    os.makedirs(sub2)
    open(sub2 + "/report.txt", "w").write("completely different and longer content")
    os.utime(sub2 + "/report.txt", (mtime_a + 500, mtime_a + 500))

    with patch(PATCH_WRITE, return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP, return_value=None), \
         patch(PATCH_SCANRES, return_value=None):
        results, _ = make_call(folderA, folderB, output)

    # Should appear in matches AND mismatched simultaneously
    match_names = [m[0] for m in results["matches"]]
    mismatch_names = [m[0] for m in results["mismatched"]]
    assert "report.txt" in match_names
    assert "report.txt" in mismatch_names

def test_hash_only_mode_different_sizes_same_hash(folders, monkeypatch):
    """HASH-ONLY: force different sizes via scan results so accurate mode skipped."""
    folderA, folderB, output = folders

    import src.engine.compare_engine as engine_module  # ← patch via engine
    import os
    monkeypatch.setattr(engine_module.config, "HASH_ONLY_MODE", True)
    monkeypatch.setattr(engine_module.config, "HASH_COMPARE_MODE", False)
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT", False)

    real_pathA = folderA + "/file.txt"
    real_pathB = folderB + "/file.txt"
    open(real_pathA, "w").write("identical content")
    open(real_pathB, "w").write("different content here")

    real_size  = os.path.getsize(real_pathA)
    real_mtime = os.path.getmtime(real_pathA)

    mock_filesA = {"file.txt": (real_pathA, real_size, real_mtime)}
    mock_filesB = {"file.txt": [(real_pathB, real_size + 999, real_mtime + 999)]}

    with patch("src.engine.compare_engine.scan_folder",
               side_effect=[mock_filesA, mock_filesB]), \
         patch(PATCH_WRITE,   return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP,    return_value=None), \
         patch(PATCH_SCANRES, return_value=None):
        results, _ = make_call(folderA, folderB, output)

    assert len(results["mismatched"]) == 1

def test_file_with_no_candidates_goes_to_missing(folders, monkeypatch):
    """File in A has zero candidates in B — hits line 111 missing.append."""
    folderA, folderB, output = folders

    import src.engine.compare_engine as engine_module  # ← patch via engine
    import os
    monkeypatch.setattr(engine_module.config, "HASH_ONLY_MODE", False)
    monkeypatch.setattr(engine_module.config, "HASH_COMPARE_MODE", False)
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT", False)

    real_pathA = folderA + "/ghost.txt"
    open(real_pathA, "w").write("only in A")
    real_size  = os.path.getsize(real_pathA)
    real_mtime = os.path.getmtime(real_pathA)

    mock_filesA = {"ghost.txt": (real_pathA, real_size, real_mtime)}
    mock_filesB = {}

    with patch("src.engine.compare_engine.scan_folder",
               side_effect=[mock_filesA, mock_filesB]), \
         patch(PATCH_WRITE,   return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP,    return_value=None), \
         patch(PATCH_SCANRES, return_value=None):
        results, _ = make_call(folderA, folderB, output)

    missing_names = [m[0] for m in results["missing"]]
    assert "ghost.txt" in missing_names

def test_returns_source_and_target_counts(folders, monkeypatch):
    """Results dict should contain source and target file counts."""
    folderA, folderB, output = folders

    import src.engine.compare_engine as engine_module  # ← patch via engine
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT", False)

    # Create 2 files in source, 3 in target
    open(folderA + "/file1.txt", "w").write("content")
    open(folderA + "/file2.txt", "w").write("content")
    open(folderB + "/file1.txt", "w").write("content")
    open(folderB + "/file2.txt", "w").write("content")
    open(folderB + "/file3.txt", "w").write("content")

    with patch(PATCH_WRITE, return_value=None), \
            patch(PATCH_SUMMARY, return_value=""), \
            patch(PATCH_DUMP, return_value=None), \
            patch(PATCH_SCANRES, return_value=None):
        results, _ = make_call(folderA, folderB, output)

    assert "source_count" in results
    assert "target_count" in results
    assert "source_unique" in results
    assert "target_unique" in results
    assert results["source_count"] == 2
    assert results["target_count"] == 3
    assert results["source_unique"] == 2
    assert results["target_unique"] == 3

def test_compare_folders_handles_walk_error(folders, monkeypatch):
    """Should handle os.walk failure gracefully and default counts to 0."""
    folderA, folderB, output = folders

    import src.engine.compare_engine as engine_module  # ← patch via engine
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT", False)

    original_walk = os.walk
    call_count = 0

    def fake_walk(path, *args, **kwargs):
        nonlocal call_count
        call_count += 1
        # First 2 calls are scan_folder — let them succeed
        # 3rd and 4th calls are os.walk counts — make them fail
        if call_count >= 3:
            raise OSError("Walk failed")
        return original_walk(path, *args, **kwargs)

    monkeypatch.setattr(engine_module.os, "walk", fake_walk)

    with patch(PATCH_WRITE,   return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP,    return_value=None), \
         patch(PATCH_SCANRES, return_value=None):
        results, _ = make_call(folderA, folderB, output)

    assert results["source_count"] == 0
    assert results["target_count"] == 0

def test_timestamped_output_creates_subfolder(folders, monkeypatch):
    """When TIMESTAMPED_OUTPUT=True engine creates timestamped subfolder."""
    folderA, folderB, output = folders

    import src.engine.compare_engine as engine_module
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT", True)
    monkeypatch.setattr(engine_module.config, "HASH_ONLY_MODE", False)
    monkeypatch.setattr(engine_module.config, "HASH_COMPARE_MODE", False)
    monkeypatch.setattr(engine_module.config, "FIND_ALL_LOCATIONS_MODE", True)

    open(folderA + "/file.txt", "w").write("content")
    open(folderB + "/file.txt", "w").write("content")

    with patch(PATCH_WRITE,   return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP,    return_value=None), \
         patch(PATCH_SCANRES, return_value=None):
        results, _ = make_call(folderA, folderB, output)

    # Verify a timestamped subfolder was created inside output
    import os
    subfolders = os.listdir(output)
    assert len(subfolders) == 1
    assert len(subfolders[0]) == 15  # YYYYMMDD_HHMMSS format

def test_delete_exact_match_calls_handle_delete(folders, monkeypatch):
    """DELETE_EXACT_MATCHES=True should call handle_delete on matched file."""
    folderA, folderB, output = folders
    import src.engine.compare_engine as engine_module
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT",    False)
    monkeypatch.setattr(engine_module.config, "HASH_ONLY_MODE",        False)
    monkeypatch.setattr(engine_module.config, "HASH_COMPARE_MODE",     False)
    monkeypatch.setattr(engine_module.config, "FIND_ALL_LOCATIONS_MODE", True)
    monkeypatch.setattr(engine_module.config, "DELETE_EXACT_MATCHES",  True)
    monkeypatch.setattr(engine_module.config, "DELETE_CANDIDATES",     False)
    monkeypatch.setattr(engine_module.config, "DRY_RUN",               False)

    open(folderA + "/file.txt", "w").write("same content")
    open(folderB + "/file.txt", "w").write("same content")
    import os
    os.utime(folderA + "/file.txt", (1000, 1000))
    os.utime(folderB + "/file.txt", (1000, 1000))

    with patch(PATCH_WRITE,   return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP,    return_value=None), \
         patch(PATCH_SCANRES, return_value=None), \
         patch("src.engine.compare_engine.handle_delete") as mock_delete:
        results, _ = make_call(folderA, folderB, output)

    assert mock_delete.called


def test_dry_run_match_does_not_call_handle_delete(folders, monkeypatch):
    """DRY_RUN=True should not call handle_delete on matched file."""
    folderA, folderB, output = folders
    import src.engine.compare_engine as engine_module
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT",    False)
    monkeypatch.setattr(engine_module.config, "HASH_ONLY_MODE",        False)
    monkeypatch.setattr(engine_module.config, "HASH_COMPARE_MODE",     False)
    monkeypatch.setattr(engine_module.config, "FIND_ALL_LOCATIONS_MODE", True)
    monkeypatch.setattr(engine_module.config, "DELETE_EXACT_MATCHES",  True)
    monkeypatch.setattr(engine_module.config, "DELETE_CANDIDATES",     False)
    monkeypatch.setattr(engine_module.config, "DRY_RUN",               True)

    open(folderA + "/file.txt", "w").write("same content")
    open(folderB + "/file.txt", "w").write("same content")
    import os
    os.utime(folderA + "/file.txt", (1000, 1000))
    os.utime(folderB + "/file.txt", (1000, 1000))

    with patch(PATCH_WRITE,   return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP,    return_value=None), \
         patch(PATCH_SCANRES, return_value=None), \
         patch("src.engine.compare_engine.handle_delete") as mock_delete:
        results, _ = make_call(folderA, folderB, output)

    assert not mock_delete.called


def test_delete_candidate_calls_handle_delete(folders, monkeypatch):
    """DELETE_CANDIDATES=True should call handle_delete on mismatched file."""
    folderA, folderB, output = folders
    import src.engine.compare_engine as engine_module
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT",    False)
    monkeypatch.setattr(engine_module.config, "HASH_ONLY_MODE",        False)
    monkeypatch.setattr(engine_module.config, "HASH_COMPARE_MODE",     False)
    monkeypatch.setattr(engine_module.config, "FIND_ALL_LOCATIONS_MODE", True)
    monkeypatch.setattr(engine_module.config, "DELETE_EXACT_MATCHES",  False)
    monkeypatch.setattr(engine_module.config, "DELETE_CANDIDATES",     True)
    monkeypatch.setattr(engine_module.config, "DRY_RUN",               False)

    open(folderA + "/file.txt", "w").write("version A")
    open(folderB + "/file.txt", "w").write("version B")
    import os
    os.utime(folderA + "/file.txt", (1000, 1000))
    os.utime(folderB + "/file.txt", (2000, 2000))  # different timestamp = mismatch

    with patch(PATCH_WRITE,   return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP,    return_value=None), \
         patch(PATCH_SCANRES, return_value=None), \
         patch("src.engine.compare_engine.handle_delete") as mock_delete:
        results, _ = make_call(folderA, folderB, output)

    assert mock_delete.called


def test_dry_run_candidate_does_not_call_handle_delete(folders, monkeypatch):
    """DRY_RUN=True should not call handle_delete on mismatched file."""
    folderA, folderB, output = folders
    import src.engine.compare_engine as engine_module
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT",    False)
    monkeypatch.setattr(engine_module.config, "HASH_ONLY_MODE",        False)
    monkeypatch.setattr(engine_module.config, "HASH_COMPARE_MODE",     False)
    monkeypatch.setattr(engine_module.config, "FIND_ALL_LOCATIONS_MODE", True)
    monkeypatch.setattr(engine_module.config, "DELETE_EXACT_MATCHES",  False)
    monkeypatch.setattr(engine_module.config, "DELETE_CANDIDATES",     True)
    monkeypatch.setattr(engine_module.config, "DRY_RUN",               True)

    open(folderA + "/file.txt", "w").write("version A")
    open(folderB + "/file.txt", "w").write("version B")
    import os
    os.utime(folderA + "/file.txt", (1000, 1000))
    os.utime(folderB + "/file.txt", (2000, 2000))

    with patch(PATCH_WRITE,   return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP,    return_value=None), \
         patch(PATCH_SCANRES, return_value=None), \
         patch("src.engine.compare_engine.handle_delete") as mock_delete:
        results, _ = make_call(folderA, folderB, output)

    assert not mock_delete.called

def test_quarantine_exact_match_calls_handle_delete(folders, monkeypatch):
    """USE_QUARANTINE=True should call handle_delete with quarantine_dir for matched file."""
    folderA, folderB, output = folders
    import src.engine.compare_engine as engine_module
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT",    False)
    monkeypatch.setattr(engine_module.config, "HASH_ONLY_MODE",        False)
    monkeypatch.setattr(engine_module.config, "HASH_COMPARE_MODE",     False)
    monkeypatch.setattr(engine_module.config, "FIND_ALL_LOCATIONS_MODE", True)
    monkeypatch.setattr(engine_module.config, "DELETE_EXACT_MATCHES",  True)
    monkeypatch.setattr(engine_module.config, "DELETE_CANDIDATES",     False)
    monkeypatch.setattr(engine_module.config, "DRY_RUN",               False)
    monkeypatch.setattr(engine_module.config, "USE_QUARANTINE",        True)

    open(folderA + "/file.txt", "w").write("same content")
    open(folderB + "/file.txt", "w").write("same content")
    import os
    os.utime(folderA + "/file.txt", (1000, 1000))
    os.utime(folderB + "/file.txt", (1000, 1000))

    with patch(PATCH_WRITE,   return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP,    return_value=None), \
         patch(PATCH_SCANRES, return_value=None), \
         patch("src.engine.compare_engine.handle_delete") as mock_delete:
        results, _ = make_call(folderA, folderB, output)

    assert mock_delete.called
    _, kwargs = mock_delete.call_args
    assert "quarantine" in kwargs["quarantine_dir"]

def test_quarantine_candidate_calls_handle_delete(folders, monkeypatch):
    """USE_QUARANTINE=True should call handle_delete with quarantine_dir for mismatched file."""
    folderA, folderB, output = folders
    import src.engine.compare_engine as engine_module
    monkeypatch.setattr(engine_module.config, "TIMESTAMPED_OUTPUT",    False)
    monkeypatch.setattr(engine_module.config, "HASH_ONLY_MODE",        False)
    monkeypatch.setattr(engine_module.config, "HASH_COMPARE_MODE",     False)
    monkeypatch.setattr(engine_module.config, "FIND_ALL_LOCATIONS_MODE", True)
    monkeypatch.setattr(engine_module.config, "DELETE_EXACT_MATCHES",  False)
    monkeypatch.setattr(engine_module.config, "DELETE_CANDIDATES",     True)
    monkeypatch.setattr(engine_module.config, "DRY_RUN",               False)
    monkeypatch.setattr(engine_module.config, "USE_QUARANTINE",        True)

    open(folderA + "/file.txt", "w").write("version A")
    open(folderB + "/file.txt", "w").write("version B")
    import os
    os.utime(folderA + "/file.txt", (1000, 1000))
    os.utime(folderB + "/file.txt", (2000, 2000))

    with patch(PATCH_WRITE,   return_value=None), \
         patch(PATCH_SUMMARY, return_value=""), \
         patch(PATCH_DUMP,    return_value=None), \
         patch(PATCH_SCANRES, return_value=None), \
         patch("src.engine.compare_engine.handle_delete") as mock_delete:
        results, _ = make_call(folderA, folderB, output)

    assert mock_delete.called
    _, kwargs = mock_delete.call_args
    assert "quarantine" in kwargs["quarantine_dir"]
