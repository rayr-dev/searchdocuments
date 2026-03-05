# tests/test_config.py

import src.config as config

# -----------------------------
# Default value tests
# -----------------------------
def test_default_diagnostic_mode():
    assert not config.DIAGNOSTIC_MODE

def test_default_diag_scan():
    assert not config.DIAG_SCAN

def test_default_diag_compare():
    assert not config.DIAG_COMPARE

def test_default_diag_writers():
    assert not config.DIAG_WRITERS

def test_default_find_all_locations_mode():
    assert config.FIND_ALL_LOCATIONS_MODE

def test_default_timestamped_output():
    assert config.TIMESTAMPED_OUTPUT

def test_default_silent_mode():
    assert not config.SILENT_MODE

def test_default_hash_compare_mode():
    assert not config.HASH_COMPARE_MODE

def test_default_hash_only_mode():
    assert not config.HASH_ONLY_MODE

def test_default_dry_run():
    assert not config.DRY_RUN

def test_default_use_quarantine():
    assert not config.USE_QUARANTINE

def test_default_delete_exact_matches():
    assert not config.DELETE_EXACT_MATCHES

def test_default_delete_candidates():
    assert not config.DELETE_CANDIDATES

# -----------------------------
# initialize_runtime tests
# -----------------------------
def test_initialize_runtime_resets_diagnostic_mode():
    config.DIAGNOSTIC_MODE = True
    config.initialize_runtime()
    assert not config.DIAGNOSTIC_MODE

def test_initialize_runtime_resets_hash_only_mode():
    config.HASH_ONLY_MODE = True
    config.initialize_runtime()
    assert not config.HASH_ONLY_MODE

def test_initialize_runtime_resets_hash_compare_mode():
    config.HASH_COMPARE_MODE = True
    config.initialize_runtime()
    assert not config.HASH_COMPARE_MODE

def test_initialize_runtime_resets_dry_run():
    config.DRY_RUN = True
    config.initialize_runtime()
    assert not config.DRY_RUN

def test_initialize_runtime_resets_use_quarantine():
    config.USE_QUARANTINE = True
    config.initialize_runtime()
    assert not config.USE_QUARANTINE

def test_initialize_runtime_resets_delete_exact_matches():
    config.DELETE_EXACT_MATCHES = True
    config.initialize_runtime()
    assert not config.DELETE_EXACT_MATCHES

def test_initialize_runtime_resets_delete_candidates():
    config.DELETE_CANDIDATES = True
    config.initialize_runtime()
    assert not config.DELETE_CANDIDATES

def test_initialize_runtime_resets_find_all_locations():
    config.FIND_ALL_LOCATIONS_MODE = True
    config.initialize_runtime()
    assert config.FIND_ALL_LOCATIONS_MODE

def test_initialize_runtime_resets_timestamped_output():
    config.TIMESTAMPED_OUTPUT = False
    config.initialize_runtime()
    assert config.TIMESTAMPED_OUTPUT  # resets to True not False

def test_initialize_runtime_resets_silent_mode():
    config.SILENT_MODE = True
    config.initialize_runtime()
    assert not config.SILENT_MODE

def test_initialize_runtime_resets_diag_scan():
    config.DIAG_SCAN = True
    config.initialize_runtime()
    assert not config.DIAG_SCAN

def test_initialize_runtime_resets_diag_compare():
    config.DIAG_COMPARE = True
    config.initialize_runtime()
    assert not config.DIAG_COMPARE

def test_initialize_runtime_resets_diag_writers():
    config.DIAG_WRITERS = True
    config.initialize_runtime()
    assert not config.DIAG_WRITERS

def test_initialize_runtime_resets_all_at_once():
    """Set all flags then confirm initialize_runtime resets everything."""
    config.DIAGNOSTIC_MODE = True
    config.HASH_ONLY_MODE = True
    config.HASH_COMPARE_MODE = True
    config.DRY_RUN = True
    config.USE_QUARANTINE = True
    config.DELETE_EXACT_MATCHES = True
    config.DELETE_CANDIDATES = True
    config.FIND_ALL_LOCATIONS_MODE = False
    config.SILENT_MODE = True
    config.DIAG_SCAN = True
    config.DIAG_COMPARE = True
    config.DIAG_WRITERS = True

    config.initialize_runtime()

    assert not config.DIAGNOSTIC_MODE
    assert not config.HASH_ONLY_MODE
    assert not config.HASH_COMPARE_MODE
    assert not config.DRY_RUN
    assert not config.USE_QUARANTINE
    assert not config.DELETE_EXACT_MATCHES
    assert not config.DELETE_CANDIDATES
    assert config.FIND_ALL_LOCATIONS_MODE
    assert not config.SILENT_MODE
    assert not config.DIAG_SCAN
    assert not config.DIAG_COMPARE
    assert not config.DIAG_WRITERS
    assert config.TIMESTAMPED_OUTPUT  # only flag that resets to True
