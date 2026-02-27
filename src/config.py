# config.py

# -----------------------------------------
# Global diagnostic and runtime flags
# -----------------------------------------

# Master diagnostic switch
DIAGNOSTIC_MODE = False
# Optional: fine-grained diagnostic categories
DIAG_SCAN = False
DIAG_COMPARE = False
DIAG_WRITERS = False

# Compare Behavior
FIND_ALL_LOCATIONS_MODE = False

#Output Behavior
TIMESTAMPED_OUTPUT = True   # Suppress all console output
SILENT_MODE = False          # Supress console output

# Hash comparison modes #DEFAULT IS TIMESTAMP ONLY
HASH_COMPARE_MODE = False    # timestamp+size first, then hash confirm
HASH_ONLY_MODE = False      # hash everything, ignore timestamp+size

# Deletion/ quarantine
DRY_RUN = False
USE_QUARANTINE = False
DELETE_EXACT_MATCHES = False
DELETE_CANDIDATES = False

DIAGNOSTIC_MODE = False


def initialize_runtime():
    """Reset all runtime flags to their default values."""
    global DIAGNOSTIC_MODE
    global DIAG_SCAN, DIAG_COMPARE, DIAG_WRITERS
    global FIND_ALL_LOCATIONS_MODE
    global HASH_COMPARE_MODE, HASH_ONLY_MODE
    global TIMESTAMPED_OUTPUT, SILENT_MODE
    global DRY_RUN, USE_QUARANTINE
    global DELETE_EXACT_MATCHES, DELETE_CANDIDATES

    # Diagnostics
    DIAGNOSTIC_MODE = False
    DIAG_SCAN = False
    DIAG_COMPARE = False
    DIAG_WRITERS = False

    # Comparison behavior
    FIND_ALL_LOCATIONS_MODE = False

    # Hash modes
    HASH_COMPARE_MODE = False
    HASH_ONLY_MODE = False

    # Output behavior
    TIMESTAMPED_OUTPUT = True
    SILENT_MODE = False

    # Deletion / quarantine
    DRY_RUN = False
    USE_QUARANTINE = False
    DELETE_EXACT_MATCHES = False
    DELETE_CANDIDATES = False
