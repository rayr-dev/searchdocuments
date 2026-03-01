# tests/conftest.py
import pytest
import os
import tempfile
import shutil
import random
import string

@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    try:
        yield d
    finally:
        shutil.rmtree(d, ignore_errors=True)

@pytest.fixture
def temp_output_dir():
    """
    Creates a temporary directory for Excel/CSV/Text output.
    Automatically cleaned up after each test.
    """
    d = tempfile.mkdtemp(prefix="recon_output_")
    try:
        yield d
    finally:
        shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def sample_results():
    """
    Provides a consistent set of comparison results for output tests.
    """
    matches = [
        ("match1.txt", "A/match1.txt", "B/match1.txt")
    ]

    mismatched = [
        ("mismatch1.txt", "A/mismatch1.txt",
         [("B/mismatch1.txt", 1000, 500)])
    ]

    missing = [
        ("missing1.txt", "A/missing1.txt")
    ]

    return matches, mismatched, missing


@pytest.fixture
def read_file():
    """
    Helper fixture to read back CSV or text output.
    """
    def _reader(path):
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    return _reader

# tests/conftest.py (add below your other fixtures)

def _random_filename():
    """Generate a random filename with safe characters."""
    name = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return f"{name}.txt"


def _random_content():
    """Generate random file content."""
    length = random.randint(5, 200)
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


@pytest.fixture
def randomized_folder_structure():
    """
    Creates a randomized folder structure for stress-testing:
      - Random files in A
      - Random files in B
      - Some matches
      - Some mismatches
      - Some missing files
      - Some duplicates in B
    Returns (folderA, folderB, manifest)
    """
    root = tempfile.mkdtemp(prefix="recon_random_")
    folderA = os.path.join(root, "A")
    folderB = os.path.join(root, "B")

    os.makedirs(folderA, exist_ok=True)
    os.makedirs(folderB, exist_ok=True)

    manifest = {
        "matches": [],
        "mismatches": [],
        "missing": [],
        "duplicates": []
    }

    try:
        # Number of files to generate
        count = random.randint(5, 20)

        for _ in range(count):
            fname = _random_filename()

            # Decide file type
            mode = random.choice(["match", "mismatch", "missing", "duplicate"])

            # MATCH
            if mode == "match":
                content = _random_content()
                with open(os.path.join(folderA, fname), "w") as f:
                    f.write(content)
                with open(os.path.join(folderB, fname), "w") as f:
                    f.write(content)
                manifest["matches"].append(fname)

            # MISMATCH
            elif mode == "mismatch":
                with open(os.path.join(folderA, fname), "w") as f:
                    f.write(_random_content())
                with open(os.path.join(folderB, fname), "w") as f:
                    f.write(_random_content())
                manifest["mismatches"].append(fname)

            # MISSING (exists only in A)
            elif mode == "missing":
                with open(os.path.join(folderA, fname), "w") as f:
                    f.write(_random_content())
                manifest["missing"].append(fname)

            # DUPLICATE (multiple copies in B)
            elif mode == "duplicate":
                content = _random_content()
                with open(os.path.join(folderA, fname), "w") as f:
                    f.write(content)

                # Create 2–3 duplicates in B
                dup_count = random.randint(2, 3)
                dup_paths = []
                for i in range(dup_count):
                    subdir = os.path.join(folderB, f"copy{i}")
                    os.makedirs(subdir, exist_ok=True)
                    path = os.path.join(subdir, fname)
                    with open(path, "w") as f:
                        f.write(content)
                    dup_paths.append(path)

                manifest["duplicates"].append((fname, dup_paths))

        yield folderA, folderB, manifest

    finally:
        shutil.rmtree(root, ignore_errors=True)

# tests/conftest.py (append below your other fixtures)

def _randname():
    return ''.join(random.choices(string.ascii_lowercase, k=8)) + ".txt"


@pytest.fixture
def randomized_deletion_environment():
    """
    Creates a randomized environment for testing deletion/quarantine logic.

    Structure:
      root/
        A/   (source folder)
        B/   (target folder with files to delete/quarantine)
        Q/   (quarantine folder)

    Produces:
      - Random files in B
      - Random subset flagged as "candidates"
      - Optional corrupt files
      - Optional permission-denied files (simulated)
    """
    root = tempfile.mkdtemp(prefix="recon_del_")
    folderA = os.path.join(root, "A")
    folderB = os.path.join(root, "B")
    quarantine = os.path.join(root, "Q")

    os.makedirs(folderA, exist_ok=True)
    os.makedirs(folderB, exist_ok=True)
    os.makedirs(quarantine, exist_ok=True)

    # Create random files in B
    file_count = random.randint(5, 15)
    files_b = []

    for _ in range(file_count):
        fname = _randname()
        path = os.path.join(folderB, fname)
        with open(path, "w") as f:
            f.write("".join(random.choices(string.ascii_letters, k=50)))
        files_b.append(path)

    # Random subset flagged as deletion candidates
    candidate_count = random.randint(1, len(files_b))
    candidates = random.sample(files_b, candidate_count)

    # Optional corrupt files
    corrupt_files = []
    if random.choice([True, False]):
        fname = _randname()
        path = os.path.join(folderB, fname)
        with open(path, "wb") as f:
            f.write(b"\x00\xFF\x00\xFF")  # binary garbage
        corrupt_files.append(path)
        candidates.append(path)

    # Optional permission-denied simulation
    permission_denied = []
    if random.choice([True, False]):
        fname = _randname()
        path = os.path.join(folderB, fname)
        with open(path, "w") as f:
            f.write("locked file")
        os.chmod(path, 0o000)  # remove permissions
        permission_denied.append(path)
        candidates.append(path)

    manifest = {
        "folderA": folderA,
        "folderB": folderB,
        "quarantine": quarantine,
        "files_b": files_b,
        "candidates": candidates,
        "corrupt": corrupt_files,
        "permission_denied": permission_denied,
    }

    try:
        yield manifest
    finally:
        # Restore permissions so cleanup succeeds
        for p in permission_denied:
            try:
                os.chmod(p, 0o777)
            except Exception:
                pass

        shutil.rmtree(root, ignore_errors=True)
