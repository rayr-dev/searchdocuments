# utilities/scan_folders.py
# System
import os

# Local
from utilities.logging_setup import diag

def scan_folder(folder, multi=False):
    results = {}

    for root, dirs, files in os.walk(folder):
        for filename in files:
            full_path = os.path.join(root, filename)

            try:
                size = os.path.getsize(full_path)
                mtime = os.path.getmtime(full_path)
            except Exception as error:
                diag(f"SCAN: Skipping unreadable file: {full_path} ({error})")
                continue

            if multi:
                # MULTI-MATCH MODE (folderB)
                results.setdefault(filename, []).append((full_path, size, mtime))
                diag(f"SCAN: Adding B candidate for {filename}: {full_path}")
            else:
                # SINGLE-MATCH MODE (folderA)
                results[filename] = (full_path, size, mtime)
                diag(f"SCAN: Adding A file {filename}: {full_path}")

    return results


def dump_scan_results(filesA, filesB):
    diag("\n================ SCAN RESULTS ================")
    diag(f"Scan Source files = {len(filesA)}")
    diag(f"Scan Target files = {len(filesB)}")

    diag("\n--- FILES A ---")
    for key, value in filesA.items():
        diag(f"  A key: {key}")
        diag(f"    {value}")

    diag("\n--- FILES B ---")
    for key, value in filesB.items():
        diag(f"  B key: {key}")
        for entry in value:
            diag(f"    {entry}")

    diag("\n==============================================\n")
    diag("Dump Scan Results: ")
