import os
from utilities.diagnostics import diag

def scan_folder(folder, multi=False):
    results = {}

    for root, dirs, files in os.walk(folder):
        for filename in files:
            full_path = os.path.join(root, filename)

            try:
                size = os.path.getsize(full_path)
                mtime = os.path.getmtime(full_path)
            except Exception as e:
                diag(f"SCAN: Skipping unreadable file: {full_path} ({e})")
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
    print("\n================ SCAN RESULTS ================")

    print("\n--- FILES A ---")
    for key, value in filesA.items():
        print(f"  A key: {key}")
        print(f"    {value}")

    print("\n--- FILES B ---")
    for key, value in filesB.items():
        print(f"  B key: {key}")
        for entry in value:
            print(f"    {entry}")

    print("\n==============================================\n")