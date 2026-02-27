import os


def build_summary(output_dir, matches, mismatched, missing,
                  progress_callback=None, status_callback=None):
    summary_path = os.path.join(output_dir, "summary.txt")

    if status_callback:
        status_callback(f"Writing Summary report to: {summary_path}")
    if progress_callback:
        progress_callback(95)

    # Build summary text using the same logic as print_summary
    total_matches = len(matches)
    total_mismatches = len(mismatched)
    total_missing = len(missing)

    from collections import Counter
    match_names = [name for name, _, _ in matches]
    multi_match_counts = Counter(match_names)
    multi_match_cases = sum(1 for k, v in multi_match_counts.items() if v > 1)

    mismatch_names = {name for name, _, _ in mismatched}
    mixed_cases = sum(1 for name in mismatch_names if name in multi_match_counts)

    lines = []
    lines.append("=============== SUMMARY REPORT ===============")
    lines.append(f"Total Exact Matches:     {total_matches}")
    lines.append(f"Total Mismatches:        {total_mismatches}")
    lines.append(f"Total Missing Files:     {total_missing}")
    lines.append("")
    lines.append(f"Multi-Match Cases:       {multi_match_cases}")
    lines.append(f"Mixed Match/Mismatch:    {mixed_cases}")
    lines.append("==============================================")

    summary_text = "\n".join(lines)

    with open(summary_path, "w", encoding="utf-8", errors="replace") as f:
        f.write(summary_text)

    if status_callback:
        status_callback("Summary report written.")


def print_summary(matches, mismatched, missing, status_callback=None):
    total_matches = len(matches)
    total_mismatches = len(mismatched)
    total_missing = len(missing)

    from collections import Counter
    match_names = [name for name, _, _ in matches]
    multi_match_counts = Counter(match_names)
    multi_match_cases = sum(1 for k, v in multi_match_counts.items() if v > 1)

    mismatch_names = {name for name, _, _ in mismatched}
    mixed_cases = sum(1 for name in mismatch_names if name in multi_match_counts)

    summary = [
        "=============== SUMMARY REPORT ===============",
        f"Total Exact Matches:     {total_matches}",
        f"Total Mismatches:        {total_mismatches}",
        f"Total Missing Files:     {total_missing}",
        "",
        f"Multi-Match Cases:       {multi_match_cases}",
        f"Mixed Match/Mismatch:    {mixed_cases}",
        "=============================================="
    ]

    summary_text = "\n".join(summary)

    return summary_text
