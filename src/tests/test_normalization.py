# ============================================================
#  tests/test_normalization.py
# ============================================================

import unittest
from Search-documents import clean_filename, normalize_path
import unicodedata
import os

class TestNormalization(unittest.TestCase):

    def test_clean_filename_removes_invisible_chars(self):
        dirty = "file\u200B\u200E\u202Aname.txt"
        cleaned = clean_filename(dirty)
        self.assertEqual(cleaned, "filename.txt")

    def test_clean_filename_collapses_spaces(self):
        dirty = "my   file   name.txt"
        cleaned = clean_filename(dirty)
        self.assertEqual(cleaned, "my file name.txt")

    def test_normalize_path_adds_longpath_prefix(self):
        p = os.path.abspath("example.txt")
        normalized = normalize_path(p)
        self.assertTrue(normalized.startswith("\\\\?\\"))

    def test_normalize_path_normalizes_unicode(self):
        composed = "café.txt"
        decomposed = unicodedata.normalize("NFD", composed)
        normalized = normalize_path(decomposed)
        self.assertEqual(
            unicodedata.normalize("NFC", normalized[4:]),  # strip \\?\
            unicodedata.normalize("NFC", os.path.abspath(composed))
        )

if __name__ == "__main__":
    unittest.main()