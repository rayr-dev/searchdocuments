# ============================================================
# 1. IMPORTS
# ============================================================

import os
import sys
import csv
import hashlib
import unicodedata
import shutil
import time
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import PatternFill

import tkinter as tk
from tkinter import filedialog, messagebox


# ============================================================
# 2. GLOBAL FLAGS
# ============================================================

HASH_ONLY_MODE = False
FIND_ALL_LOCATIONS_MODE = False

DRY_RUN = True
DELETE_EXACT_MATCHES = False
DELETE_CANDIDATES = False
USE_QUARANTINE = True

LOG_FILE = "file_compare_deletions.log"


# ============================================================
# 3. UTILITY FUNCTIONS
# ============================================================

def clean_filename(name: str) -> str:
    """
    Normalize filename to a safe, comparable form.
    """
    if not isinstance(name, str):
        name = str(name)
    name = unicodedata.normalize("NFC", name)
    return name.strip()


def normalize_path(path: str) -> str:
    """
    Normalize paths for consistent comparison.
    """
    return os.path.normpath(os.path.abspath(path))


def file_hash(path: str) -> str:
    """
    Compute SHA-256 hash of a file.
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def write_log(msg: str) -> None:
    """
    Append a line to the deletion/quarantine log.
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8", errors="replace") as f:
            f.write(line)
    except Exception:
        # Logging must never crash the app
        pass


# ============================================================
# 4. FOLDER SCANNING
# ============================================================

def scan_folder(folder: str, multi: bool = False):
    """
    Scan a folder recursively.

    If multi=False:
        returns dict[relpath] = (fullpath, size, mtime)
    If multi=True:
        returns dict[relpath] = list[(fullpath, size, mtime)]
    """
    folder = normalize_path(folder)
    result = {}

    for root, _, files in os.walk(folder):
        for name in files:
            full = os.path.join(root, name)
            rel = os.path.relpath(full, folder)
            rel = clean_filename(rel)
            try:
                st = os.stat(full)
            except OSError:
                continue
            size = st.st_size
            mtime = st.st_mtime

            if multi:
                result.setdefault(rel, []).append((full, size, mtime))
            else:
                result[rel] = (full, size, mtime)

    return result


# ============================================================
# 5. COMPARISON ENGINE
# ============================================================

def compare_folders_recursive(folderA: str,
                              folderB: str,
                              excel_output: str = "comparison.xlsx",
                              csv_output: str = "comparison.csv",
                              text_output: str = "comparison.txt"):
    """
    Core comparison engine.

    Returns:
        matches:    list[(name, pathA, pathB)]
        mismatched: list[(name, pathA, list[(pathB, sizeB, mtimeB)])]
        missing:    list[(name, pathA)]
    """
    folderA = normalize_path(folderA)
    folderB = normalize_path(folderB)

    # A: single entry per relpath
    filesA = scan_folder(folderA, multi=False)

    # B: possibly multiple entries per relpath
    filesB = scan_folder(folderB, multi=True)

    matches = []
    mismatched = []
    missing = []

    for rel, (pathA, sizeA, mtimeA) in filesA.items():
        candidatesB = filesB.get(rel)

        if not candidatesB:
            missing.append((rel, pathA))
            continue

        # If we only care about first match (non multi-location mode)
        if not FIND_ALL_LOCATIONS_MODE:
            candidatesB = [candidatesB[0]]

        # Evaluate each candidate
        local_matches = []
        local_mismatches = []

        # Precompute hash for A only if needed
        hashA = None

        for pathB, sizeB, mtimeB in candidatesB:
            is_match = False

            if HASH_ONLY_MODE:
                if hashA is None:
                    hashA = file_hash(pathA)
                hashB = file_hash(pathB)
                is_match = (hashA == hashB)
            else:
                # Timestamp + size first
                if sizeA == sizeB and abs(mtimeA - mtimeB) <= 1.0:
                    is_match = True
                else:
                    # If sizes match, we can optionally hash to confirm mismatch
                    if sizeA == sizeB:
                        if hashA is None:
                            hashA = file_hash(pathA)
                        hashB = file_hash(pathB)
                        is_match = (hashA == hashB)

            if is_match:
                local_matches.append((rel, pathA, pathB))
            else:
                local_mismatches.append((pathB, sizeB, mtimeB))

        if local_matches:
            matches.extend(local_matches)

        if local_mismatches:
            mismatched.append((rel, pathA, local_mismatches))

    # Write outputs
    write_excel_output(excel_output, matches, mismatched, missing)
    write_csv_output(csv_output, matches, mismatched, missing)
    write_text_output(text_output, matches, mismatched, missing)

    # Process deletions/quarantine if enabled
    process_deletions(matches, mismatched)

    return matches, mismatched, missing


# ============================================================
# 6. OUTPUT WRITERS
# ============================================================

def write_excel_output(path, matches, mismatched, missing):
    wb = Workbook()
    ws = wb.active
    ws.title = "Comparison"

    header = [
        "Status",
        "Filename",
        "Path A",
        "Timestamp A",
        "Path B",
        "Timestamp B",
    ]
    ws.append(header)

    green = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
    yellow = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
    red = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

    # Matches
    for name, pathA, pathB in matches:
        try:
            tsA = datetime.fromtimestamp(os.path.getmtime(pathA)).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            tsA = ""
        try:
            tsB = datetime.fromtimestamp(os.path.getmtime(pathB)).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            tsB = ""

        row = ["Exact Match", name, pathA, tsA, pathB, tsB]
        ws.append(row)
        for cell in ws[ws.max_row]:
            cell.fill = green

    # Mismatches
    for name, pathA, b_list in mismatched:
        try:
            tsA = datetime.fromtimestamp(os.path.getmtime(pathA)).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            tsA = ""
        for pathB, _, _ in b_list:
            try:
                tsB = datetime.fromtimestamp(os.path.getmtime(pathB)).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                tsB = ""
            row = ["Mismatch", name, pathA, tsA, pathB, tsB]
            ws.append(row)
            for cell in ws[ws.max_row]:
                cell.fill = yellow

    # Missing
    for name, pathA in missing:
        try:
            tsA = datetime.fromtimestamp(os.path.getmtime(pathA)).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            tsA = ""
        row = ["Missing in Folder B", name, pathA, tsA, "", ""]
        ws.append(row)
        for cell in ws[ws.max_row]:
            cell.fill = red

    wb.save(path)


def write_csv_output(path, matches, mismatched, missing):
    with open(path, "w", newline="", encoding="utf-8", errors="replace") as f:
        writer = csv.writer(f)
        writer.writerow(["Status", "Filename", "Path A", "Timestamp A", "Path B", "Timestamp B"])

        # Matches
        for name, pathA, pathB in matches:
            try:
                tsA = datetime.fromtimestamp(os.path.getmtime(pathA)).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                tsA = ""
            try:
                tsB = datetime.fromtimestamp(os.path.getmtime(pathB)).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                tsB = ""
            writer.writerow(["Exact Match", name, pathA, tsA, pathB, tsB])

        # Mismatches
        for name, pathA, b_list in mismatched:
            try:
                tsA = datetime.fromtimestamp(os.path.getmtime(pathA)).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                tsA = ""
            for pathB, _, _ in b_list:
                try:
                    tsB = datetime.fromtimestamp(os.path.getmtime(pathB)).strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    tsB = ""
                writer.writerow(["Mismatch", name, pathA, tsA, pathB, tsB])

        # Missing
        for name, pathA in missing:
            try:
                tsA = datetime.fromtimestamp(os.path.getmtime(pathA)).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                tsA = ""
            writer.writerow(["Missing in Folder B", name, pathA, tsA, "", ""])


def write_text_output(path, matches, mismatched, missing):
    with open(path, "w", encoding="utf-8", errors="replace") as f:
        f.write("=== Exact Matches ===\n")
        for name, pathA, pathB in matches:
            f.write(f"{name}\n  A: {pathA}\n  B: {pathB}\n\n")

        f.write("\n=== Mismatches ===\n")
        for name, pathA, b_list in mismatched:
            f.write(f"{name}\n  A: {pathA}\n")
            for pathB, sizeB, mtimeB in b_list:
                tsB = datetime.fromtimestamp(mtimeB).strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"  B: {pathB} (size={sizeB}, ts={tsB})\n")
            f.write("\n")

        f.write("\n=== Missing in Folder B ===\n")
        for name, pathA in missing:
            f.write(f"{name}\n  A: {pathA}\n\n")


# ============================================================
# 7. DELETION / QUARANTINE ENGINE
# ============================================================

def ensure_quarantine() -> str:
    """
    Ensure a quarantine folder exists next to the EXE/script.
    """
    base = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else __file__)
    q = os.path.join(base, "Quarantine")
    os.makedirs(q, exist_ok=True)
    return q


def _delete_or_quarantine(path: str, reason: str):
    """
    Delete or move a file based on global flags.
    """
    action = "DRY-RUN"
    if DRY_RUN:
        write_log(f"[DRY-RUN] Would handle: {path} ({reason})")
        return

    if USE_QUARANTINE:
        q = ensure_quarantine()
        base = os.path.basename(path)
        target = os.path.join(q, base)
        try:
            shutil.move(path, target)
            action = f"QUARANTINED -> {target}"
        except Exception as e:
            write_log(f"[ERROR] Failed to quarantine {path}: {e}")
            return
    else:
        try:
            os.remove(path)
            action = "DELETED"
        except Exception as e:
            write_log(f"[ERROR] Failed to delete {path}: {e}")
            return

    write_log(f"[{action}] {path} ({reason})")


def process_deletions(matches, mismatched):
    """
    Apply deletion/quarantine rules based on global flags.
    """
    # Exact matches
    if DELETE_EXACT_MATCHES:
        for _, _, pathB in matches:
            _delete_or_quarantine(pathB, "Exact Match")

    # Mismatch candidates
    if DELETE_CANDIDATES:
        for _, _, b_list in mismatched:
            for pathB, _, _ in b_list:
                _delete_or_quarantine(pathB, "Mismatch Candidate")


# ============================================================
# 8. GUI LAUNCHER
# ============================================================

def launch_gui():
    # Handle splash (PyInstaller)
    pyi_splash = None
    if getattr(sys, 'frozen', False):
        try:
            import pyi_splash as _ps
            pyi_splash = _ps
        except Exception:
            pyi_splash = None

    root = tk.Tk()
    root.title("Reconciliation Tool")
    root.geometry("600x450")
    root.resizable(False, False)

    # -----------------------------
    # Folder Selection
    # -----------------------------
    folderA_var = tk.StringVar()
    folderB_var = tk.StringVar()

    def browse_folderA():
        path = filedialog.askdirectory()
        if path:
            folderA_var.set(path)

    def browse_folderB():
        path = filedialog.askdirectory()
        if path:
            folderB_var.set(path)

    tk.Label(root, text="Folder A (Source):", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=20, pady=(20, 0))
    tk.Entry(root, textvariable=folderA_var, width=60).pack(anchor="w", padx=20)
    tk.Button(root, text="Browse", command=browse_folderA).pack(anchor="w", padx=20, pady=(0, 10))

    tk.Label(root, text="Folder B (Target):", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=20)
    tk.Entry(root, textvariable=folderB_var, width=60).pack(anchor="w", padx=20)
    tk.Button(root, text="Browse", command=browse_folderB).pack(anchor="w", padx=20, pady=(0, 20))

    # -----------------------------
    # Comparison Options
    # -----------------------------
    tk.Label(root, text="Comparison Options:", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=20)

    compare_mode_var = tk.StringVar(value="timestamp")

    tk.Radiobutton(root, text="Timestamp + Size (Fastest)", variable=compare_mode_var, value="timestamp").pack(anchor="w", padx=40)
    tk.Radiobutton(root, text="Hash Comparison (Accurate)", variable=compare_mode_var, value="hash").pack(anchor="w", padx=40)
    tk.Radiobutton(root, text="Hash-Only Mode", variable=compare_mode_var, value="hash_only").pack(anchor="w", padx=40)

    find_all_var = tk.BooleanVar()
    tk.Checkbutton(root, text="Find All Locations in Folder B", variable=find_all_var).pack(anchor="w", padx=40, pady=(0, 10))

    # -----------------------------
    # Deletion / Quarantine Options
    # -----------------------------
    tk.Label(root, text="Cleanup Options:", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=20)

    dry_run_var = tk.BooleanVar(value=True)
    delete_matches_var = tk.BooleanVar()
    delete_candidates_var = tk.BooleanVar()
    quarantine_var = tk.BooleanVar(value=True)

    tk.Checkbutton(root, text="Dry Run (No Changes Made)", variable=dry_run_var).pack(anchor="w", padx=40)
    tk.Checkbutton(root, text="Delete Exact Matches", variable=delete_matches_var).pack(anchor="w", padx=40)
    tk.Checkbutton(root, text="Delete Mismatch Candidates", variable=delete_candidates_var).pack(anchor="w", padx=40)
    tk.Checkbutton(root, text="Use Quarantine Folder", variable=quarantine_var).pack(anchor="w", padx=40)

    # -----------------------------
    # Run Button
    # -----------------------------
    def run_comparison():
        folderA = folderA_var.get().strip()
        folderB = folderB_var.get().strip()

        if not folderA or not folderB:
            messagebox.showerror("Error", "Please select both Folder A and Folder B.")
            return

        if not os.path.isdir(folderA) or not os.path.isdir(folderB):
            messagebox.showerror("Error", "One or both selected folders are invalid.")
            return

        global HASH_ONLY_MODE, FIND_ALL_LOCATIONS_MODE
        global DRY_RUN, DELETE_EXACT_MATCHES, DELETE_CANDIDATES, USE_QUARANTINE

        mode = compare_mode_var.get()
        HASH_ONLY_MODE = (mode == "hash_only")
        # If "hash" selected, we still use timestamp+size + hash confirm; HASH_ONLY_MODE stays False.

        FIND_ALL_LOCATIONS_MODE = find_all_var.get()

        DRY_RUN = dry_run_var.get()
        DELETE_EXACT_MATCHES = delete_matches_var.get()
        DELETE_CANDIDATES = delete_candidates_var.get()
        USE_QUARANTINE = quarantine_var.get()

        try:
            compare_folders_recursive(
                folderA,
                folderB,
                excel_output="comparison.xlsx",
                csv_output="comparison.csv",
                text_output="comparison.txt"
            )
            messagebox.showinfo("Done", "Comparison complete. Output files created.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")

    tk.Button(root, text="Run Comparison", font=("Segoe UI", 11, "bold"), width=20, command=run_comparison).pack(pady=20)

    # -----------------------------
    # Close splash screen AFTER GUI is ready
    # -----------------------------
    if getattr(sys, 'frozen', False) and pyi_splash:
        try:
            pyi_splash.close()
        except Exception:
            pass

    root.mainloop()


# ============================================================
# 9. ENTRY POINT
# ============================================================

if __name__ == "__main__":
    # If no arguments → GUI mode
    if len(sys.argv) == 1:
        launch_gui()
    else:
        # CLI mode: python Search-documents.py <FolderA> <FolderB>
        folderA = sys.argv[1]
        folderB = sys.argv[2]
        compare_folders_recursive(
            folderA,
            folderB,
            excel_output="comparison.xlsx",
            csv_output="comparison.csv",
            text_output="comparison.txt"
        )