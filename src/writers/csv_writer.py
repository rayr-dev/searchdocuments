# writes/csv_writers.py
# System
import os
import csv
import logging

from datetime import datetime


# Local
from utilities.logging_setup import diag

def write_csv_output(output_dir,
                     matches,
                     mismatched,
                     missing,
                     progress_callback=None,
                     status_callback=None
                     ):

    diag("CSV_WRITER/write_csv_output")
    csv_path = os.path.join(output_dir, "comparison.csv")

    if status_callback:
        status_callback(f"Writing CSV report to: {csv_path}")
    if progress_callback:
        progress_callback(75)

    try:
        with open(csv_path, "w", newline="", encoding="utf-8", errors="replace") as f:
            writer = csv.writer(f)
            writer.writerow(["Status", "Filename", "Path A", "Timestamp A", "Path B", "Timestamp B", "Action"])

            # ------------------------------------------------------------
            # Exact Matches
            # ------------------------------------------------------------
            for name, pathA, pathB, action in matches:

                if not pathA or not os.path.exists(pathA):
                    diag(f"CSV: Skipping invalid pathA for match: {pathA}")
                    continue
                if not pathB or not os.path.exists(pathB):
                    diag(f"CSV: Skipping invalid pathB for match: {pathB}")
                    continue

                try:
                    tsA = datetime.fromtimestamp(os.path.getmtime(pathA)).strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    tsA = ""
                try:
                    tsB = datetime.fromtimestamp(os.path.getmtime(pathB)).strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    tsB = ""

                writer.writerow(["Exact Match", name, pathA, tsA, pathB, tsB, action or ""])

            # ------------------------------------------------------------
            # Mismatches
            # ------------------------------------------------------------
            for name, pathA, b_list, action in mismatched:

                if not pathA or not os.path.exists(pathA):
                    diag(f"CSV: Skipping invalid pathA for mismatch: {pathA}")
                    continue

                try:
                    tsA = datetime.fromtimestamp(os.path.getmtime(pathA)).strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    tsA = ""

                for pathB, _, _ in b_list:

                    if not pathB or not os.path.exists(pathB):
                        diag(f"CSV: Skipping invalid pathB for mismatch: {pathB}")
                        continue

                    try:
                        tsB = datetime.fromtimestamp(os.path.getmtime(pathB)).strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        tsB = ""

                    writer.writerow(["Mismatch", name, pathA, tsA, pathB, tsB, action or ""])

            # ------------------------------------------------------------
            # Missing Files
            # ------------------------------------------------------------
            for name, pathA in missing:

                if not pathA or not os.path.exists(pathA):
                    diag(f"CSV: Skipping invalid pathA for missing: {pathA}")
                    continue

                try:
                    tsA = datetime.fromtimestamp(os.path.getmtime(pathA)).strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    tsA = ""

                writer.writerow(["Missing in Folder B", name, pathA, tsA, "", ""])
    except Exception as e:
        diag(f"ERROR writing CSV report: {e}")
        logging.error(f"Error writing CSV report {csv_path} - Exception: {e}")
    diag("CSV_WRITER/write_csv_output ending")
