# writers/writer_all_reports. py

# System
import os
import logging

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
    diag("WRITE_ALL_REPORTS/write_all_reports Starting")

    # Ensure output directory exists
    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as error:
        diag(f"ERROR: Could not create output directory: {output_dir} ({error})")
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
    except Exception as error:
        diag(f"ERROR writing Excel report: {error}")
        logging.error(f"ERROR writing Excel report: {error}")
        if status_callback:
            status_callback(f"ERROR writing Excel report: {error}")

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
    except Exception as error:
        diag("ERROR writing CSV report: {error}")
        logging.error(f"ERROR writing CSV report: {error}")
        if status_callback:
            status_callback(f"ERROR writing CSV report: {error}")

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
    except Exception as error:
        diag(f"ERROR writing Text report: {error}")
        logging.error(f"ERROR writing Text report: {error}")
        if status_callback:
            status_callback(f"ERROR writing Text report: {error}")


    # Write summary.txt
    build_summary(output_dir, matches, mismatched, missing,
                     progress_callback, status_callback)

    # Final status
    if status_callback:
        status_callback(f"Reports written to: {output_dir}")

    diag("WRITE_ALL_REPORTS/write_all_reports ending")
