# utilities/diagnostics_old.py
import os
import json
import config

def diag(msg):
    if config.DIAGNOSTIC_MODE:
        print(f"[DIAG] {msg}")

def dump_diagnostics(matches, mismatched, missing, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    data = {
        "matches": matches,
        "mismatched": mismatched,
        "missing": missing
    }

    out_path = os.path.join(output_folder, "diagnostics.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return out_path
