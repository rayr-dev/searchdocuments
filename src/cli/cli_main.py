# cli/cli_main.py

import argparse
import sys
import config
from orchestrator import run_reconciliation
from utilities.diagnostics import diag
from writers.summary_writer import print_summary


def build_parser():
    parser = argparse.ArgumentParser(
        description="Reconciliation Tool - Command Line Interface"
    )

    parser.add_argument("folderA", help="Source folder (Folder A)")
    parser.add_argument("folderB", help="Target folder (Folder B)")

    parser.add_argument(
        "-o", "--output",
        help="Output directory for reports",
        required=True
    )

    # Comparison modes
    parser.add_argument(
        "--hash",
        action="store_true",
        help="Enable hash comparison mode (accurate)"
    )

    parser.add_argument(
        "--hashonly",
        action="store_true",
        help="Enable hash-only mode"
    )

    # Output options
    parser.add_argument(
        "--findall",
        action="store_true",
        help="Find all locations in Folder B"
    )

    # Cleanup options
    parser.add_argument(
        "--dryrun",
        action="store_true",
        help="Dry run (no changes made)"
    )

    parser.add_argument(
        "--deletematches",
        action="store_true",
        help="Delete exact matches"
    )

    parser.add_argument(
        "--deletecandidates",
        action="store_true",
        help="Delete mismatch candidates"
    )

    parser.add_argument(
        "--quarantine",
        action="store_true",
        help="Use quarantine folder instead of deleting"
    )

    # Diagnostics
    parser.add_argument(
        "--diag",
        action="store_true",
        help="Enable diagnostic output"
    )

    return parser


def run_cli():
    parser = build_parser()
    args = parser.parse_args()

    # Reset config
    config.initialize_runtime()

    # Apply comparison modes
    config.HASH_ONLY_MODE = args.hashonly
    config.HASH_COMPARE_MODE = args.hash
    # timestamp mode = default when both are False

    # Apply output options
    config.FIND_ALL_LOCATIONS_MODE = args.findall

    # Apply cleanup options
    config.DRY_RUN = args.dryrun
    config.DELETE_EXACT_MATCHES = args.deletematches
    config.DELETE_CANDIDATES = args.deletecandidates
    config.USE_QUARANTINE = args.quarantine

    # Diagnostics
    config.DIAGNOSTIC_MODE = args.diag

    diag("CLI invoked")
    diag(f"FolderA: {args.folderA}")
    diag(f"FolderB: {args.folderB}")
    diag(f"Output: {args.output}")
    diag(f"HashOnly: {config.HASH_ONLY_MODE}")
    diag(f"HashCompare: {config.HASH_COMPARE_MODE}")
    diag(f"FindAll: {config.FIND_ALL_LOCATIONS_MODE}")
    diag(f"DryRun: {config.DRY_RUN}")
    diag(f"DeleteExact: {config.DELETE_EXACT_MATCHES}")
    diag(f"DeleteCandidates: {config.DELETE_CANDIDATES}")
    diag(f"UseQuarantine: {config.USE_QUARANTINE}")

    try:
        results, summary_text = run_reconciliation(
            args.folderA,
            args.folderB,
            args.output,
            progress_callback=None,
            status_callback=None
        )

    except Exception as e:
        print(f"ERROR: {e}")
        diag(f"CLI ERROR: {e}")
        sys.exit(1)
    # Print summary once, after successful run
    print(f"\nReports written to: {args.output}")
    print_summary(summary_text)
