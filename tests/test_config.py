# tests/test_config.py

import src.config as config

# -----------------------------
# Default value tests
# -----------------------------
def test_default_diagnostic_mode():
    assert config.DIAGNOSTIC_MODE == False

def test_default_diag_scan():
    assert config.DIAG_SCAN == False

def test_default_diag_compare():
    assert config.DIAG_COMPARE == False

def test_default_diag_writers():
    assert config.DIAG_WRITERS == False

def test_default_find_all_locations_mode():
    assert config.FIND_ALL_LOCATIONS_MODE == True

def test_default_timestamped_output():
    assert config.TIMESTAMPED_OUTPUT == True

def test_default_silent_mode():
    assert config.SILENT_MODE == False

def test_default_hash_compare_mode():
    assert config.HASH_COMPARE_MODE == False

def test_default_hash_only_mode():
    assert config.HASH_ONLY_MODE == False

def test_default_dry_run():
    assert config.DRY_RUN == False

def test_default_use_quarantine():
    assert config.USE_QUARANTINE == False

def test_default_delete_exact_matches():
    assert config.DELETE_EXACT_MATCHES == False

def test_default_delete_candidates():
    assert config.DELETE_CANDIDATES == False

# -----------------------------
# initialize_runtime tests
# -----------------------------
def test_initialize_runtime_resets_diagnostic_mode():
    config.DIAGNOSTIC_MODE = True
    config.initialize_runtime()
    assert config.DIAGNOSTIC_MODE == False

def test_initialize_runtime_resets_hash_only_mode():
    config.HASH_ONLY_MODE = True
    config.initialize_runtime()
    assert config.HASH_ONLY_MODE == False

def test_initialize_runtime_resets_hash_compare_mode():
    config.HASH_COMPARE_MODE = True
    config.initialize_runtime()
    assert config.HASH_COMPARE_MODE == False

def test_initialize_runtime_resets_dry_run():
    config.DRY_RUN = True
    config.initialize_runtime()
    assert config.DRY_RUN == False

def test_initialize_runtime_resets_use_quarantine():
    config.USE_QUARANTINE = True
    config.initialize_runtime()
    assert config.USE_QUARANTINE == False

def test_initialize_runtime_resets_delete_exact_matches():
    config.DELETE_EXACT_MATCHES = True
    config.initialize_runtime()
    assert config.DELETE_EXACT_MATCHES == False

def test_initialize_runtime_resets_delete_candidates():
    config.DELETE_CANDIDATES = True
    config.initialize_runtime()
    assert config.DELETE_CANDIDATES == False

def test_initialize_runtime_resets_find_all_locations():
    config.FIND_ALL_LOCATIONS_MODE = True
    config.initialize_runtime()
    assert config.FIND_ALL_LOCATIONS_MODE == True

def test_initialize_runtime_resets_timestamped_output():
    config.TIMESTAMPED_OUTPUT = False
    config.initialize_runtime()
    assert config.TIMESTAMPED_OUTPUT == True  # resets to True not False

def test_initialize_runtime_resets_silent_mode():
    config.SILENT_MODE = True
    config.initialize_runtime()
    assert config.SILENT_MODE == False

def test_initialize_runtime_resets_diag_scan():
    config.DIAG_SCAN = True
    config.initialize_runtime()
    assert config.DIAG_SCAN == False

def test_initialize_runtime_resets_diag_compare():
    config.DIAG_COMPARE = True
    config.initialize_runtime()
    assert config.DIAG_COMPARE == False

def test_initialize_runtime_resets_diag_writers():
    config.DIAG_WRITERS = True
    config.initialize_runtime()
    assert config.DIAG_WRITERS == False

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

    assert config.DIAGNOSTIC_MODE == False
    assert config.HASH_ONLY_MODE == False
    assert config.HASH_COMPARE_MODE == False
    assert config.DRY_RUN == False
    assert config.USE_QUARANTINE == False
    assert config.DELETE_EXACT_MATCHES == False
    assert config.DELETE_CANDIDATES == False
    assert config.FIND_ALL_LOCATIONS_MODE == True
    assert config.SILENT_MODE == False
    assert config.DIAG_SCAN == False
    assert config.DIAG_COMPARE == False
    assert config.DIAG_WRITERS == False
    assert config.TIMESTAMPED_OUTPUT == True  # only flag that resets to True
