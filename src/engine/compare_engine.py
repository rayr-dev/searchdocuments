# engine/compare_engine.py
'''
The purpose performs the business logic layer to perform the comparison and returns:
results = {
    "matches" : matches,
    "mismatched" : mismatched,
    "missing" : missing
    }
    Summary_text is the output summary to display in the UI layers.
'''

# System
import os
import config
import logging

#local
from utilities.logging_setup import dump_diagnostics
from utilities.scan_folder import dump_scan_results
from utilities.path_utils import file_hash
from utilities.logging_setup import diag
from utilities.output import create_timestamped_folder
from utilities.scan_folder import scan_folder
from writers.write_all_reports import write_all_reports
from writers.summary_writer import print_summary

def compare_folders_recursive(folderA,
                              folderB,
                              output_dir,
                              progress_callback=None,
                              status_callback=None,
                              *,
                              return_results=True,
                              return_summary=True
                              ):
    diag("COMPARE_ENGINE/compare_folders_recursive: Starting compare_folders_recursive")

    # Apply timestamped output behavior ONCE
    if config.TIMESTAMPED_OUTPUT:
        output_dir = create_timestamped_folder(output_dir)

    if status_callback:
        status_callback("Scanning folders...")

    # Results from SCAN
    filesA = scan_folder(folderA, multi=False)
    filesB = scan_folder(folderB, multi=True)

    # Count actual physical files using os.walk
    try:
        source_count = sum(len(files) for _, _, files in os.walk(folderA))
        target_count = sum(len(files) for _, _, files in os.walk(folderB))
    except Exception as error:
        logging.error(f"Error counting files: {error}")
        source_count = 0
        target_count = 0

    diag(f"SCAN: FolderA physical files = {source_count}")
    diag(f"SCAN: FolderB physical files = {target_count}")
    diag(f"SCAN: FolderA unique filenames = {len(filesA)}")
    diag(f"SCAN: FolderB unique filenames = {len(filesB)}")

    dump_scan_results(filesA, filesB)

    if progress_callback:
        progress_callback(20)

    matches = []
    mismatched = []
    missing = []

    # ------------------------------------------------------------
    # Main comparison loop
    # ------------------------------------------------------------
    for rel, (pathA, sizeA, mtimeA) in filesA.items():

        candidatesB = filesB.get(rel, [])
        if not candidatesB:
            diag(f"NO CANDIDATES FOUND - MISSING: {rel}")
            missing.append((rel, pathA))
            continue

        found_match = False
        mismatch_list = []

        for pathB, sizeB, mtimeB in candidatesB:
            diag(f"COMPARE LOOP: {rel}")

            # HASH ONLY MODE - ignore timestamp completely
            if config.HASH_ONLY_MODE:  # pragma: no cover
                diag(f"INSIDE HASH_ONLY_MODE: {rel}")
                hashA = file_hash(pathA)  # pragma: no cover
                hashB = file_hash(pathB)  # pragma: no cover
                if hashA == hashB:  # pragma: no cover
                    diag(f"HASH ONLY MODE - Hashes match: {rel}")
                    matches.append((rel, pathA, pathB))
                    found_match = True
                    continue  # pragma: no cover
                # If hash doesn't match fall through to mismatch
                diag(f"HASH ONLY MODE - Hashes differ: {rel}")  # pragma: no cover
                mismatch_list.append((pathB, sizeB, mtimeB))  # pragma: no cover
                continue  # pragma: no cover

            # TIMESTAMP + SIZE MATCH - always first step for non hash-only modes
            if sizeA == sizeB and abs(mtimeA - mtimeB) <= 1.0:
                diag(f"MATCH ON TIMESTAMP: {rel} (timestamp+size)")

                if config.HASH_COMPARE_MODE:
                    # ACCURATE MODE - confirm timestamp match with hash
                    diag(f"HASH_COMPARE_MODE - confirming with hash: {rel}")
                    hashA = file_hash(pathA)
                    hashB = file_hash(pathB)
                    if hashA == hashB:
                        diag(f"HASH CONFIRMED MATCH: {rel}")
                        matches.append((rel, pathA, pathB))
                        found_match = True
                        continue
                    else:
                        diag(f"HASH REJECTED TIMESTAMP MATCH: {rel}")
                        mismatch_list.append((pathB, sizeB, mtimeB))
                        continue
                else:
                    # FAST MODE - timestamp+size match is sufficient
                    diag(f"FAST MODE MATCH: {rel}")
                    matches.append((rel, pathA, pathB))
                    found_match = True
                    continue

            # SAME SIZE but timestamp differs - try hash if accurate mode
            if sizeA == sizeB and config.HASH_COMPARE_MODE:
                diag(f"SAME SIZE DIFF TIMESTAMP - trying hash: {rel}")
                hashA = file_hash(pathA)
                hashB = file_hash(pathB)
                if hashA == hashB:
                    diag(f"HASH MATCH ON SAME SIZE: {rel}")
                    matches.append((rel, pathA, pathB))
                    found_match = True
                    continue
                else:
                    diag(f"HASH MISMATCH ON SAME SIZE: {rel}")
                    mismatch_list.append((pathB, sizeB, mtimeB))
                    continue

            # Otherwise mismatch
            diag(f"OTHER MISMATCH: {rel} vs {pathB}")
            mismatch_list.append((pathB, sizeB, mtimeB))

        # FINAL DECISION
        if found_match:
            diag("FOUND MATCH IF Processing")
            # We DO NOT suppress mismatches anymore.
            # Mixed cases should show both matches and mismatches.
            if mismatch_list:
                diag(f"FOUND MISMATCH: {rel}")
                mismatched.append((rel, pathA, mismatch_list))
        else:
            # No matches at all
            if mismatch_list:
                diag(f"NO MATCH FOUND - MISMATCHED: {rel}")
                mismatched.append((rel, pathA, mismatch_list))
            else:
                diag(f"NO MATCH and NO MISMATCH: {rel}") # pragma: no cover
                missing.append((rel, pathA)) # pragma: no cover

    if progress_callback:
        progress_callback(50)

    # ------------------------------------------------------------
    # DIAGNOSTIC DUMP
    # ------------------------------------------------------------
    dump_diagnostics(
        {
            "matches" : matches,
            "mismatched": mismatched,
            "missing" : missing
        },
        output_dir
    )

    # ------------------------------------------------------------
    # Write reports
    # ------------------------------------------------------------
    if status_callback:
        status_callback("Writing reports...")

    diag("WRITING: Starting report generation")

    write_all_reports(
        output_dir,
        matches,
        mismatched,
        missing,
        source_count=source_count,
        target_count=target_count,
        source_unique=len(filesA),
        target_unique=len(filesB),
        status_callback=status_callback,
        progress_callback=progress_callback
    )
    diag("WRITING: Reports complete")

    if status_callback:
        status_callback("Comparison complete.")

    results = {
        "matches": matches,
        "mismatched": mismatched,
        "missing": missing,
        "source_count" : source_count,
        "target_count" : target_count,
        "source_unique" : len(filesA),
        "target_unique" : len(filesB)
    }
    diag("COMPARE_ENGINE/compare_folders_recursive: Ending compare_folders_recursive")
    # Build Summary Report
    summary_text = print_summary(
        matches,
        mismatched,
        missing,
        source_count=source_count,
        target_count=target_count,
        source_unique=len(filesA),
        target_unique=len(filesB),
        status_callback=status_callback
    )
    return results, summary_text
