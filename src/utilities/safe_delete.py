# utilities/safe_delete.py
# System
import os
import shutil
import config
import logging

# Local
from utilities.logging_setup import diag

# Safe deleter (respects DRY_RUN)
def safe_delete(path: str):
    if config.DRY_RUN:
        diag(f"[DRY RUN] Would delete: {path}")
        return

    try:
        os.remove(path)
        diag(f"Deleted: {path}")
    except Exception as error:
        diag(f"ERROR deleting {path}: {error}")
        logging.error("Error deleting {path}: {error}")

# Safe move to quarantine
def move_to_quarantine(path: str, quarantine_dir: str):
    if config.DRY_RUN:
        diag(f"[DRY RUN] Would quarantine: {path}")
        return

    try:
        os.makedirs(quarantine_dir, exist_ok=True)
        dest = os.path.join(quarantine_dir, os.path.basename(path))
        shutil.move(path, dest)
        diag(f"Quarantined: {path} -> {dest}")
    except Exception as error:
        diag(f"ERROR quarantining {path}: {error}")
        logging.error("Error quarantining {path}: {error}")

# Decide delete v. quarantine
def handle_delete(path: str, quarantine_dir: str = None):
    if config.USE_QUARANTINE and quarantine_dir:
        move_to_quarantine(path, quarantine_dir)
    else:
        safe_delete(path)
    diag(f"Safe_Delete Path: {path}")
# Timestamp mismatch delete candidate
def is_delete_candidate(fileA, fileB):
    diag(f"Is delete candidate: {fileA} and {fileB}")
    return (
        fileA.size == fileB.size and
        fileA.timestamp != fileB.timestamp
    )
