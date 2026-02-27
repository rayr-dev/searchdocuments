# ============================================================
#  tests/test_hashing.py
# ============================================================

import unittest
from unittest.mock import mock_open, patch
from Search-documents import file_hash
import hashlib


class TestHashing(unittest.TestCase):

    def test_hash_small_file(self):
        """
        Ensures hashing a small file produces the correct SHA-256 digest.
        """
        data = b"hello world"
        expected = hashlib.sha256(data).hexdigest()

        m = mock_open(read_data=data)

        with patch("builtins.open", m):
            digest = file_hash("dummy.txt")

        self.assertEqual(digest, expected)

    def test_hash_large_file_streaming(self):
        """
        Ensures hashing reads in chunks (streaming), not all at once.
        """
        # Simulate a large file by returning chunks
        chunks = [b"a" * 8192, b"b" * 8192, b"c" * 4096, b""]

        def chunk_reader(*args, **kwargs):
            # Iterator that yields chunks sequentially
            for c in chunks:
                yield c

        mock_file = unittest.mock.MagicMock()
        mock_file.__enter__.return_value.read = unittest.mock.MagicMock(
            side_effect=chunk_reader()
        )

        with patch("builtins.open", return_value=mock_file):
            digest = file_hash("largefile.bin")

        # Compute expected hash manually
        h = hashlib.sha256()
        h.update(b"a" * 8192)
        h.update(b"b" * 8192)
        h.update(b"c" * 4096)
        expected = h.hexdigest()

        self.assertEqual(digest, expected)

    def test_hash_file_not_found(self):
        """
        Ensures file_hash raises FileNotFoundError when file is missing.
        """
        with self.assertRaises(FileNotFoundError):
            file_hash("nonexistent.txt")


if __name__ == "__main__":
    unittest.main()