from Search-documents import compare_folders_recursive

def test_real_comparison(populate_basic_files):
    folderA, folderB = populate_basic_files

    matches, mismatched, missing = compare_folders_recursive(
        folderA, folderB,
        excel_output="out.xlsx",
        csv_output="out.csv",
        text_output="out.txt"
    )

    assert len(matches) == 1
    assert len(mismatched) == 1
    assert len(missing) == 1
    
# for multiple locations
def test_find_all_locations(populate_multi_location):
    folderA, folderB = populate_multi_location

    matches, mismatched, missing = compare_folders_recursive(
        folderA, folderB,
        excel_output="out.xlsx",
        csv_output="out.csv",
        text_output="out.txt"
    )

    assert len(matches) == 2