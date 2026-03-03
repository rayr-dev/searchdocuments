# cli/cli_main.py
'''
The purpose of this module is to process the Search Documents using the CLI Interface.
'''

# System
import sys
import argparse
import logging
import config

#Local
from orchestrator import run_reconciliation
from utilities.logging_setup import init_logging, diag


def build_parser():
    diag("CLI_MAIN/build_parser: Starting build_parser")
    parser = argparse.ArgumentParser(
        description="Search Documents Tool - Command Line Interface"
    )

    parser.add_argument("folderA",
                        help="Source folder (Folder A)"
    )
    parser.add_argument("folderB",
                        help="Target folder (Folder B)"
    )

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
    diag("CLI_MAIN/build_parser: Ending build_parser")
    return parser


def run_cli():
    diag("CLI_MAIN/run_cli: Starting run reconciliation process")
    parser = build_parser()
    args = parser.parse_args()

    # Initialize logging for CLI
    log_path = init_logging(args.output,
                            diagnostic=args.diag
                            )
    diag(f"Log file: {log_path}")

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

    diag("RUN_CLI arguments before run_reconciliation")
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
        logging.info(f"Reports written to: {args.output}")
        # Print Summary after successful run
        print(summary_text)

    except Exception as error:
        logging.error(f"Exception Error from run_reconciliation: {error}")
        diag(f"Exception Error from run_reconciliation: {error}")
        sys.exit(1)

    diag("CLI_MAIN/run_cli: End run reconciliation process")
