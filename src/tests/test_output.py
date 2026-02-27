# ============================================================
#  tests/test_output.py
# ============================================================

import unittest
from unittest.mock import patch, MagicMock, mock_open

from Search

-documents import (
    write_excel_output,
    write_csv_output,
    write_text_output
)


class TestOutputWriters(unittest.TestCase):

    # --------------------------------------------------------
    # EXCEL OUTPUT TESTS
    # --------------------------------------------------------
    @patch("Search-documents.Workbook")
    def test_excel_output_structure(self, mock_wb):
        """
        Ensures Excel output writes the correct number of rows
        and uses the correct worksheet title.
        """

        # Mock workbook + worksheet
        mock_ws = MagicMock()
        mock_wb.return_value = MagicMock(active=mock_ws)

        matches = [
            ("file1.txt", "A/file1.txt", "B/file1.txt")
        ]
        mismatched = [
            ("file2.txt", "A/file2.txt", [("B/file2.txt", 1000, 500)])
        ]
        missing = [
            ("file3.txt", "A/file3.txt")
        ]

        write_excel_output("dummy.xlsx", matches, mismatched, missing)

        # Header + 1 match + 1 mismatch + 1 missing = 4 rows
        self.assertEqual(mock_ws.append.call_count, 4)

        # Workbook saved
        mock_wb.return_value.save.assert_called_once()

    # --------------------------------------------------------
    # CSV OUTPUT TESTS
    # --------------------------------------------------------
    @patch("builtins.open", new_callable=mock_open)
    @patch("csv.writer")
    def test_csv_output(self, mock_writer, mock_file):
        """
        Ensures CSV writer is called with correct rows.
        """

        writer_instance = MagicMock()
        mock_writer.return_value = writer_instance

        matches = [
            ("file1.txt", "A/file1.txt", "B/file1.txt")
        ]
        mismatched = [
            ("file2.txt", "A/file2.txt", [("B/file2.txt", 1000, 500)])
        ]
        missing = [
            ("file3.txt", "A/file3.txt")
        ]

        write_csv_output("dummy.csv", matches, mismatched, missing)

        # Header + 3 rows = 4 calls
        self.assertEqual(writer_instance.writerow.call_count, 4)

    # --------------------------------------------------------
    # TEXT OUTPUT TESTS
    # --------------------------------------------------------
    @patch("builtins.open", new_callable=mock_open)
    def test_text_output(self, mock_file):
        """
        Ensures text output writes expected section headers.
        """

        matches = [
            ("file1.txt", "A/file1.txt", "B/file1.txt")
        ]
        mismatched = [
            ("file2.txt", "A/file2.txt", [("B/file2.txt", 1000, 500)])
        ]
        missing = [
            ("file3.txt", "A/file3.txt")
        ]

        write_text_output("dummy.txt", matches, mismatched, missing)

        handle = mock_file()

        # Validate section headers
        written = "".join(call.args[0] for call in handle.write.call_args_list)

        self.assertIn("=== EXACT MATCHES ===", written)
        self.assertIn("=== MISMATCHES ===", written)
        self.assertIn("=== MISSING IN FOLDER B ===", written)

    def test_csv_output_writes_expected_rows(temp_output_dir, sample_results, read_file):
        matches, mismatched, missing = sample_results

        csv_path = os.path.join(temp_output_dir, "out.csv")

        write_csv_output(csv_path, matches, mismatched, missing)

        content = read_file(csv_path)

        assert "Exact Match" in content
        assert "Timestamp/Size Mismatch" in content or "Hash Mismatch" in content
        assert "Missing in Folder B" in content
        
@pytest.fixture
    def fake_folder_structure():
        """
        Creates a temporary folder structure with:
          - folderA/
          - folderB/
        Returns (root, folderA, folderB)
        Automatically cleaned up after each test.
        """
        root = tempfile.mkdtemp(prefix="recon_test_")
        folderA = os.path.join(root, "A")
        folderB = os.path.join(root, "B")

        os.makedirs(folderA, exist_ok=True)
        os.makedirs(folderB, exist_ok=True)

        try:
            yield root, folderA, folderB
        finally:
        shutil.rmtree(root, ignore_errors=True)

    @pytest.fixture
    def populate_basic_files(fake_folder_structure):
        """
        Populates Folder A and Folder B with:
          - match1.txt (identical)
          - mismatch1.txt (different content)
          - missing1.txt (only in A)
        Returns (folderA, folderB)
        """
        root, folderA, folderB = fake_folder_structure

        # Exact match
        with open(os.path.join(folderA, "match1.txt"), "w") as f:
            f.write("same content")
        with open(os.path.join(folderB, "match1.txt"), "w") as f:
            f.write("same content")

        # Mismatch
        with open(os.path.join(folderA, "mismatch1.txt"), "w") as f:
            f.write("A version")
        with open(os.path.join(folderB, "mismatch1.txt"), "w") as f:
            f.write("B version")

        # Missing in B
        with open(os.path.join(folderA, "missing1.txt"), "w") as f:
            f.write("exists only in A")

        # Ensure timestamps differ slightly
        time.sleep(0.01)

    return folderA, folderB

    @pytest.fixture
    def populate_multi_location(fake_folder_structure):
        """
        Creates a scenario for Find-All-Locations mode:
          - A/file.txt
          - B/file.txt
          - B/copy/file.txt
        Returns (folderA, folderB)
        """
        root, folderA, folderB = fake_folder_structure

        # Create A/file.txt
        with open(os.path.join(folderA, "file.txt"), "w") as f:
            f.write("content")

        # Create B/file.txt
        with open(os.path.join(folderB, "file.txt"), "w") as f:
            f.write("content")

        # Create B/copy/file.txt
        copy_dir = os.path.join(folderB, "copy")
        os.makedirs(copy_dir, exist_ok=True)
        with open(os.path.join(copy_dir, "file.txt"), "w") as f:
            f.write("content")

        return folderA, folderB


if __name__ == "__main__":
    unittest.main()