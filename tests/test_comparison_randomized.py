from Search-documents import compare_folders_recursive

def test_randomized_comparison(randomized_folder_structure):
    folderA, folderB, manifest = randomized_folder_structure

    matches, mismatched, missing = compare_folders_recursive(
        folderA, folderB,
        excel_output="out.xlsx",
        csv_output="out.csv",
        text_output="out.txt"
    )

    # Validate matches
    for fname in manifest["matches"]:
        assert any(m[0] == fname for m in matches)

    # Validate mismatches
    for fname in manifest["mismatches"]:
        assert any(m[0] == fname for m in mismatched)

    # Validate missing
    for fname in manifest["missing"]:
        assert any(m[0] == fname for m in missing)

    # Validate duplicates
    for fname, dup_paths in manifest["duplicates"]:
        assert any(m[0] == fname for m in matches)