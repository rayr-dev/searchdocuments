# engine/compare_engine.py
try:
    # System
    import config
    import traceback
    import sys

    # 3rd Party

    #local
    from utilities.logging_setup import dump_diagnostics
    from utilities.scan_folder import dump_scan_results
    from utilities.path_utils import file_hash
    from utilities.logging_setup import diag
    from utilities.output import create_timestamped_folder
    from utilities.scan_folder import scan_folder
    from writers.write_all_reports import write_all_reports
    from writers.summary_writer import print_summary

except ImportError:
    traceback.print_exc()
    sys.exit(1) #exit with an error code 1


def compare_folders_recursive(folderA, folderB,
                              output_dir,
                              progress_callback=None,
                              status_callback=None,
                              *,
                              return_results=True,
                              return_summary=True
                              ):

    diag("Compare Engine: Starting run compare_folders_recursive")
    # Apply timestamped output behavior ONCE
    if config.TIMESTAMPED_OUTPUT:
        output_dir = create_timestamped_folder(output_dir)

    if status_callback:
        status_callback("Scanning folders...")

    # Results from SCAN
    filesA = scan_folder(folderA, multi=False)
    filesB = scan_folder(folderB, multi=True)

    diag(f"SCAN: FolderA files = {len(filesA)}")
    diag(f"SCAN: FolderB files = {len(filesB)}")

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
            missing.append((rel, pathA))
            continue

        found_match = False
        mismatch_list = []

        for pathB, sizeB, mtimeB in candidatesB:
            diag(f"COMPARE: {rel}")

            # TIMESTAMP + SIZE MATCH
            if sizeA == sizeB and abs(mtimeA - mtimeB) <= 1.0:
                diag(f"MATCH: {rel} (timestamp+size)")

                matches.append((rel, pathA, pathB))
                found_match = True
                # DO NOT break — allow multi-match
                continue

            # ACCURATE MODE (hash confirm)
            if sizeA == sizeB:
                diag(f"MATCH: {rel} (hash)")

                hashA = file_hash(pathA)
                hashB = file_hash(pathB)
                if hashA == hashB:
                    matches.append((rel, pathA, pathB))
                    found_match = True
                    continue

            # HASH-ONLY MODE
            if config.HASH_ONLY_MODE:
                hashA = file_hash(pathA) # pragma: no cover# pragma: no cover
                hashB = file_hash(pathB) # pragma: no cover# pragma: no cover
                if hashA == hashB: # pragma: no cover# pragma: no cover
                    matches.append((rel, pathA, pathB))
                    found_match = True
                    continue

            # Otherwise mismatch
            diag(f"MISMATCH: {rel} vs {pathB}")
            mismatch_list.append((pathB, sizeB, mtimeB))

        # FINAL DECISION
        if found_match:
            # We DO NOT suppress mismatches anymore.
            # Mixed cases should show both matches and mismatches.
            if mismatch_list:
                mismatched.append((rel, pathA, mismatch_list))
        else:
            # No matches at all
            diag(f"MISSING: {rel}")

            if mismatch_list:
                mismatched.append((rel, pathA, mismatch_list))
            else:
                missing.append((rel, pathA)) # pragma: no cover# pragma: no cover

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
        status_callback=status_callback,
        progress_callback=progress_callback
    )
    diag("WRITING: Reports complete")

    if status_callback:
        status_callback("Comparison complete.")

    results = {
        "matches": matches,
        "mismatched": mismatched,
        "missing": missing
    }

    # Build Summary Report
    summary_text = print_summary(matches, mismatched, missing, status_callback)
    return results, summary_text
