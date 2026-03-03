# orchestrator.py

# System
import os
import logging

# Local
from engine.compare_engine import compare_folders_recursive
from utilities.logging_setup import diag

def run_reconciliation(folderA, folderB, output_dir, progress_callback=None, status_callback=None):
    # All config flags should already be set by CLI or GUI


    diag("ORCHESTRATOR/run_reconciliation: Started")
    if not folderA or not folderB:
        raise ValueError("Folder A and Folder B must be provided.")

    if not os.path.isdir(folderA) or not os.path.isdir(folderB):
        raise ValueError("One or both folders are invalid.")

    results, summary_text = compare_folders_recursive(
        folderA,
        folderB,
        output_dir=output_dir,
        progress_callback=progress_callback,
        status_callback=status_callback,
        return_results=True,
        return_summary=True
    )
    diag("ORCHESTRATOR/run_reconciliation: Ended")
    if progress_callback:
        progress_callback(100)
    logging.info("run_reconciliation completed successfully")
    return results, summary_text
