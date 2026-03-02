# writers/text_writer.py

# System
import os
from datetime import datetime

# Local
from utilities.logging_setup import diag

def write_text_output(output_dir, matches, mismatched, missing,
                       progress_callback=None, status_callback=None):



    txt_path = os.path.join(output_dir, "comparison.txt")

    # Optional: writer-level status update
    if status_callback:
        status_callback(f"Writing Text report to: {txt_path}")
    if progress_callback:
        progress_callback(85)

    try:
        with open(txt_path, "w", encoding="utf-8", errors="replace") as f:

            # ------------------------------------------------------------
            # Exact Matches
            # ------------------------------------------------------------
            f.write("=== Exact Matches ===\n")

            for name, pathA, pathB in matches:

                if not pathA or not os.path.exists(pathA):
                    diag(f"Text: Skipping invalid pathA for match: {pathA}")
                    continue
                if not pathB or not os.path.exists(pathB):
                    diag(f"Text: Skipping invalid pathB for match: {pathB}")
                    continue

                f.write(f"{name}\n")
                f.write(f"  A: {pathA}\n")
                f.write(f"  B: {pathB}\n\n")

            # ------------------------------------------------------------
            # Mismatches
            # ------------------------------------------------------------
            f.write("=== Mismatches ===\n")

            for name, pathA, b_list in mismatched:

                if not pathA or not os.path.exists(pathA):
                    diag(f"Text: Skipping invalid pathA for mismatch: {pathA}")
                    continue

                try:
                    tsA = datetime.fromtimestamp(os.path.getmtime(pathA)).strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    tsA = ""

                f.write(f"{name}\n")
                f.write(f"  A: {pathA} (ts={tsA})\n")

                for pathB, sizeB, mtimeB in b_list:

                    if not pathB or not os.path.exists(pathB):
                        diag(f"Text: Skipping invalid pathB for mismatch: {pathB}")
                        continue

                    try:
                        tsB = datetime.fromtimestamp(mtimeB).strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        tsB = ""

                    f.write(f"  B: {pathB} (size={sizeB}, ts={tsB})\n")

                f.write("\n")

            # ------------------------------------------------------------
            # Missing Files
            # ------------------------------------------------------------
            f.write("=== Missing in Folder B ===\n")

            for name, pathA in missing:

                if not pathA or not os.path.exists(pathA):
                    diag(f"Text: Skipping invalid pathA for missing: {pathA}")
                    continue

                f.write(f"{name}\n")
                f.write(f"  A: {pathA}\n\n")
    except Exception as e:
        diag(f"ERROR writing Text report: {e}")
