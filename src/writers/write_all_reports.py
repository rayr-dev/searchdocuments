# writers/writer_all_reports. py

# System
import os

# Local
from writers.excel_writer import write_excel_output
from writers.csv_writer import write_csv_output
from writers.text_writer import write_text_output
from writers.summary_writer import build_summary
from utilities.logging_setup import diag

def write_all_reports(output_dir, matches, mismatched, missing,
                      status_callback=None, progress_callback=None):
    """
    Unified wrapper that writes Excel, CSV, and Text reports.
    Ensures each writer is isolated so one failure does not break the others.
    Provides consistent diagnostic output and callback handling.
    """



    # Ensure output directory exists
    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        diag(f"ERROR: Could not create output directory: {output_dir} ({e})")
        if status_callback:
            status_callback(f"ERROR: Could not create output directory: {output_dir}")
        return

    # ------------------------------------------------------------
    # Excel Writer
    # ------------------------------------------------------------
    try:
        write_excel_output(
            output_dir,
            matches,
            mismatched,
            missing,
            progress_callback=progress_callback,
            status_callback=status_callback
        )
        diag("Excel writer completed")
    except Exception as e:
        diag(f"ERROR writing Excel report: {e}")
        if status_callback:
            status_callback(f"ERROR writing Excel report: {e}")

    # ------------------------------------------------------------
    # CSV Writer
    # ------------------------------------------------------------
    try:
        write_csv_output(
            output_dir,
            matches,
            mismatched,
            missing,
            progress_callback=progress_callback,
            status_callback=status_callback
        )
        diag("CSV writer completed")
    except Exception as e:
        diag("ERROR writing CSV report: {e}")
        if status_callback:
            status_callback(f"ERROR writing CSV report: {e}")

    # ------------------------------------------------------------
    # Text Writer
    # ------------------------------------------------------------
    try:
        write_text_output(
            output_dir,
            matches,
            mismatched,
            missing,
            progress_callback=progress_callback,
            status_callback=status_callback
        )
        diag("Text writer completed")
    except Exception as e:
        diag(f"ERROR writing Text report: {e}")
        if status_callback:
            status_callback(f"ERROR writing Text report: {e}")


    # Write summary.txt
    build_summary(output_dir, matches, mismatched, missing,
                     progress_callback, status_callback)

    # Final status
    if status_callback:
        status_callback(f"Reports written to: {output_dir}")
