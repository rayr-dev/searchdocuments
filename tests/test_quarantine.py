# ============================================================
#  tests/test_comparison.py
# ============================================================

import unittest
from unittest.mock import patch
from Search-documents import compare_folders_recursive, HASH_ONLY_MODE


class TestComparisonEngine(unittest.TestCase):

    @patch("Search-documents.os.walk")
    @patch("Search-documents.os.path.getmtime")
    @patch("Search-documents.os.path.getsize")
    @patch("Search-documents.file_hash")
    def test_exact_match_timestamp(
        self, mock_hash, mock_size, mock_mtime, mock_walk
    ):
        """
        Ensures timestamp-based exact matches are detected correctly.
        """

        # Folder A structure
        mock_walk.side_effect = [
            # First call: Folder A
            [
                ("A", [], ["file1.txt"])
            ],
            # Second call: Folder B
            [
                ("B", [], ["file1.txt"])
            ]
        ]

        # Same timestamp, same size
        mock_mtime.return_value = 1000
        mock_size.return_value = 500

        # Hash should not be used
        mock_hash.return_value = "unused"

        matches, mismatched, missing = compare_folders_recursive(
            "A", "B",
            excel_output="test.xlsx",
            csv_output="test.csv",
            text_output="test.txt"
        )

        self.assertEqual(len(matches), 1)
        self.assertEqual(len(mismatched), 0)
        self.assertEqual(len(missing), 0)

    @patch("Search-documents.os.walk")
    @patch("Search-documents.os.path.getmtime")
    @patch("Search-documents.os.path.getsize")
    @patch("Search-documents.file_hash")
    def test_mismatch_detected(
        self, mock_hash, mock_size, mock_mtime, mock_walk
    ):
        """
        Ensures mismatches are detected when timestamps differ.
        """

        mock_walk.side_effect = [
            [("A", [], ["file1.txt"])],
            [("B", [], ["file1.txt"])]
        ]

        # Different timestamps
        mock_mtime.side_effect = [1000, 2000]

        # Same size
        mock_size.return_value = 500

        # Hash not used
        mock_hash.return_value = "unused"

        matches, mismatched, missing = compare_folders_recursive(
            "A", "B",
            excel_output="test.xlsx",
            csv_output="test.csv",
            text_output="test.txt"
        )

        self.assertEqual(len(matches), 0)
        self.assertEqual(len(mismatched), 1)
        self.assertEqual(len(missing), 0)

    @patch("Search-documents.os.walk")
    @patch("Search-documents.os.path.getmtime")
    @patch("Search-documents.os.path.getsize")
    @patch("Search-documents.file_hash")
    def test_missing_file(
        self, mock_hash, mock_size, mock_mtime, mock_walk
    ):
        """
        Ensures missing files are detected when A has a file B does not.
        """

        mock_walk.side_effect = [
            [("A", [], ["file1.txt"])],
            [("B", [], [])]
        ]

        mock_mtime.return_value = 1000
        mock_size.return_value = 500
        mock_hash.return_value = "unused"

        matches, mismatched, missing = compare_folders_recursive(
            "A", "B",
            excel_output="test.xlsx",
            csv_output="test.csv",
            text_output="test.txt"
        )

        self.assertEqual(len(matches), 0)
        self.assertEqual(len(mismatched), 0)
        self.assertEqual(len(missing), 1)

    @patch("Search-documents.os.walk")
    @patch("Search-documents.file_hash")
    def test_hash_only_mode(self, mock_hash, mock_walk):
        """
        Ensures hash-only mode overrides timestamp/size logic.
        """

        # Enable hash-only mode
        global HASH_ONLY_MODE
        HASH_ONLY_MODE = True

        mock_walk.side_effect = [
            [("A", [], ["file1.txt"])],
            [("B", [], ["file1.txt"])]
        ]

        # Hash matches
        mock_hash.return_value = "abc123"

        matches, mismatched, missing = compare_folders_recursive(
            "A", "B",
            excel_output="test.xlsx",
            csv_output="test.csv",
            text_output="test.txt"
        )

        self.assertEqual(len(matches), 1)
        self.assertEqual(len(mismatched), 0)
        self.assertEqual(len(missing), 0)

        # Reset mode
        HASH_ONLY_MODE = False

    @patch("Search-documents.os.walk")
    @patch("Search-documents.os.path.getmtime")
    @patch("Search-documents.os.path.getsize")
    def test_find_all_locations_mode(self, mock_size, mock_mtime, mock_walk):
        """
        Ensures find-all-locations mode returns all B-side matches.
        """

        from Search-documents import FIND_ALL_LOCATIONS_MODE
        global FIND_ALL_LOCATIONS_MODE
        FIND_ALL_LOCATIONS_MODE = True

        mock_walk.side_effect = [
            [("A", [], ["file1.txt"])],
            [("B", [], ["file1.txt", "file1.txt"])]
        ]

        mock_mtime.return_value = 1000
        mock_size.return_value = 500

        matches, mismatched, missing = compare_folders_recursive(
            "A", "B",
            excel_output="test.xlsx",
            csv_output="test.csv",
            text_output="test.txt"
        )

        # Should return both matches
        self.assertEqual(len(matches), 2)

        FIND_ALL_LOCATIONS_MODE = False


if __name__ == "__main__":
    unittest.main()