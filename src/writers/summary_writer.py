# writers/summary_writer.py
#
# System
import os
import logging

# Local
from utilities.logging_setup import diag


def build_summary(output_dir, matches, mismatched, missing,
                  source_count=0, target_count=0,progress_callback=None, status_callback=None):
    diag("SUMMARY_WRITER/build_summary Starting")
    summary_path = os.path.join(output_dir, "summary.txt")

    if status_callback:
        status_callback(f"Writing Summary report to: {summary_path}")
    if progress_callback:
        progress_callback(95)

    # Delegate to print_summary for consistent output
    summary_text = print_summary(
        matches, mismatched, missing,
        source_count=source_count,  # ← pass counts through
        target_count=target_count,
        status_callback=status_callback
    )

    with open(summary_path, "w", encoding="utf-8", errors="replace") as f:
        f.write(summary_text)

    if status_callback:
        status_callback("Summary report written.")

    diag("SUMMARY_WRITER/build_summary Ending")
    return summary_text


def print_summary(matches, mismatched, missing, source_count=0, target_count=0,status_callback=None):
    total_matches = len(matches)
    total_mismatches = len(mismatched)
    total_missing = len(missing)
    logging.info("SUMMARY_WRITER/print_summary Starting")
    diag(f"Print Summary total matches: {total_matches} - total mismatches: {total_mismatches} - total missing: {total_missing}")

    from collections import Counter
    match_names = [name for name, _, _ in matches]
    multi_match_counts = Counter(match_names)
    multi_match_cases = sum(1 for k, v in multi_match_counts.items() if v > 1)

    mismatch_names = {name for name, _, _ in mismatched}
    mixed_cases = sum(1 for name in mismatch_names if name in multi_match_counts)

    summary = [
        "=============== SUMMARY REPORT ===============",
        "",
        "Source Statistics:",
        f"   Total Files in Source: {source_count}",
        f"   Total Files in Target: {target_count}",
        "",
        "Reconciliation Results:",
        f"Total Exact Matches:     {total_matches}",
        f"Total Mismatches:        {total_mismatches}",
        f"Total Missing Files:     {total_missing}",
        "",
        f"Multi-Match Cases:       {multi_match_cases}",
        f"Mixed Match/Mismatch:    {mixed_cases}",
        ""
        "=============================================="
    ]

    summary_text = "\n".join(summary)
    diag("SUMMARY_WRITER/print_summary Ending")
    return summary_text
