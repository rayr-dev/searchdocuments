# tools/create_testdata.py
"""
Programmatically generates all smoke test scenario folders and files.
Recreates the full testdata/ directory structure for all 6 scenarios.

Usage:
    python tools/create_testdata.py
    python tools/create_testdata.py --clean   # delete and recreate all scenarios

File types included:
    .txt  - plain text documents
    .xlsx - Excel spreadsheets (minimal valid file)
    .docx - Word documents (minimal valid file)
    .pdf  - PDF documents (minimal valid file)
"""

# System
import os
import sys
import shutil
import struct
import argparse
import time

# ---------------------------------------------------------------------------
# Minimal valid binary file content generators
# ---------------------------------------------------------------------------

def make_txt(content: str) -> bytes:
    """Plain text file."""
    return content.encode("utf-8")


def make_xlsx() -> bytes:
    """
    Minimal valid XLSX file (ZIP containing [Content_Types].xml).
    Small enough for test data, recognized as valid by Excel.
    """
    import zipfile
    import io
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '</Types>')
        zf.writestr("_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"'
            ' Target="xl/workbook.xml"/>'
            '</Relationships>')
        zf.writestr("xl/workbook.xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/sheet">'
            '<sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"'
            ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/>'
            '</sheets></workbook>')
    return buf.getvalue()


def make_docx() -> bytes:
    """
    Minimal valid DOCX file (ZIP containing [Content_Types].xml).
    Recognized as a valid Word document container.
    """
    import zipfile
    import io
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml"'
            ' ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            '</Types>')
        zf.writestr("_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"'
            ' Target="word/document.xml"/>'
            '</Relationships>')
        zf.writestr("word/document.xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            '<w:body><w:p><w:r><w:t>Test Document</w:t></w:r></w:p></w:body>'
            '</w:document>')
    return buf.getvalue()


def make_pdf(content: str = "Test PDF") -> bytes:
    """
    Minimal valid PDF file.
    Recognized as a valid PDF by most readers.
    """
    body = (
        f"%PDF-1.4\n"
        f"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        f"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        f"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R"
        f"/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj\n"
        f"4 0 obj<</Length 44>>\nstream\nBT /F1 12 Tf 100 700 Td ({content}) Tj ET\nendstream\nendobj\n"
        f"5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n"
    )
    xref_offset = len(body.encode("latin-1"))
    trailer = (
        f"xref\n0 6\n"
        f"0000000000 65535 f \n"
        f"0000000009 00000 n \n"
        f"0000000058 00000 n \n"
        f"0000000115 00000 n \n"
        f"0000000274 00000 n \n"
        f"0000000370 00000 n \n"
        f"trailer<</Size 6/Root 1 0 R>>\n"
        f"startxref\n{xref_offset}\n%%EOF\n"
    )
    return (body + trailer).encode("latin-1")


# ---------------------------------------------------------------------------
# File writing helpers
# ---------------------------------------------------------------------------

def write_file(path: str, content: bytes, mtime: float = None):
    """Write binary content to path, optionally setting mtime."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(content)
    if mtime:
        os.utime(path, (mtime, mtime))


def write_text(path: str, text: str, mtime: float = None):
    write_file(path, make_txt(text), mtime)


def write_empty(path: str, mtime: float = None):
    write_file(path, b"", mtime)


def copy_file(src: str, dst: str):
    """Copy file preserving timestamps."""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)


# ---------------------------------------------------------------------------
# Base timestamps (fixed so test results are reproducible)
# ---------------------------------------------------------------------------

BASE_TIME = 1_772_599_200.0   # 2026-03-03 10:00:00 UTC (approx)
T1 = BASE_TIME
T2 = BASE_TIME + 3600         # +1 hour  (different timestamp = mismatch)


# ---------------------------------------------------------------------------
# Scenario builders
# ---------------------------------------------------------------------------

def build_scenario1(base: str):
    """
    Scenario 1 - Identical files.
    Source and target are exact copies including subfolders.
    Mixed file types: txt, xlsx, docx, pdf.
    Expected: all exact matches, 1 multi-match case.
    """
    print("  Building scenario1_same...")

    # Root level files
    for folder in ["source", "target"]:
        root = os.path.join(base, folder)
        write_text(os.path.join(root, "exact.txt"),      "Exact match content",   T1)
        write_empty(os.path.join(root, "zero size file.txt"),                      T1)
        write_file(os.path.join(root, "report.xlsx"),    make_xlsx(),              T1)
        write_file(os.path.join(root, "document.docx"),  make_docx(),              T1)
        write_file(os.path.join(root, "summary.pdf"),    make_pdf("Summary"),      T1)

    # Sub A
    for folder in ["source/Sub A", "target/Sub A"]:
        root = os.path.join(base, folder)
        write_text(os.path.join(root, "exact.txt"),     "Exact match content",    T1)
        write_file(os.path.join(root, "report.xlsx"),   make_xlsx(),               T1)

    # Sub B
    for folder in ["source/Sub B", "target/Sub B"]:
        root = os.path.join(base, folder)
        write_text(os.path.join(root, "exact.txt"),     "Exact match content",    T1)
        write_file(os.path.join(root, "document.docx"), make_docx(),               T1)


def build_scenario2(base: str):
    """
    Scenario 2 - Mixed results.
    Contains: exact matches, mismatches, missing files, multi-match, mixed match/mismatch.
    Mixed file types: txt, xlsx, docx, pdf.
    """
    print("  Building scenario2_mixed...")

    xlsx_content_a = make_xlsx()
    xlsx_content_b = make_xlsx()   # same structure, different zip timestamps = mismatch

    # Source root
    src = os.path.join(base, "source")
    write_text(os.path.join(src, "exact.txt"),       "Exact match content",      T1)
    write_text(os.path.join(src, "mismatch.txt"),    "Version A content here",   T1)
    write_text(os.path.join(src, "missing.txt"),     "Only in source",           T1)
    write_text(os.path.join(src, "mixed.txt"),       "Mixed content source",     T1)
    write_empty(os.path.join(src, "zero size file.txt"),                          T1)
    write_file(os.path.join(src, "report.xlsx"),     xlsx_content_a,             T1)
    write_file(os.path.join(src, "contract.docx"),   make_docx(),                T1)
    write_file(os.path.join(src, "invoice.pdf"),     make_pdf("Invoice A"),      T1)

    # Target root
    tgt = os.path.join(base, "target")
    write_text(os.path.join(tgt, "exact.txt"),       "Exact match content",      T1)
    write_text(os.path.join(tgt, "mismatch.txt"),    "Version B content here",   T2)  # different time
    write_text(os.path.join(tgt, "mixed.txt"),       "Mixed content source",     T1)
    write_empty(os.path.join(tgt, "zero size file.txt"),                          T1)
    write_file(os.path.join(tgt, "report.xlsx"),     xlsx_content_b,             T2)  # different time
    write_file(os.path.join(tgt, "contract.docx"),   make_docx(),                T1)
    write_file(os.path.join(tgt, "invoice.pdf"),     make_pdf("Invoice B"),      T2)  # different time

    # Source Sub A
    src_a = os.path.join(base, "source/Sub A")
    write_text(os.path.join(src_a, "exact.txt"),     "Exact match content",      T1)
    write_text(os.path.join(src_a, "mismatch.txt"),  "Version A content here",   T1)
    write_text(os.path.join(src_a, "missing.txt"),   "Only in source",           T1)
    write_text(os.path.join(src_a, "mixed.txt"),     "Mixed content source",     T1)
    write_file(os.path.join(src_a, "report.xlsx"),   xlsx_content_a,             T1)

    # Target Sub A
    tgt_a = os.path.join(base, "target/Sub A")
    write_text(os.path.join(tgt_a, "exact.txt"),     "Exact match content",      T1)
    write_text(os.path.join(tgt_a, "mismatch.txt"),  "Version B content here",   T2)
    write_text(os.path.join(tgt_a, "mixed.txt"),     "Mixed content source",     T1)
    write_empty(os.path.join(tgt_a, "zero size file.txt"),                        T1)
    write_file(os.path.join(tgt_a, "report.xlsx"),   xlsx_content_b,             T2)

    # Source Sub B
    src_b = os.path.join(base, "source/Sub B")
    write_text(os.path.join(src_b, "exact.txt"),     "Exact match content",      T1)
    write_text(os.path.join(src_b, "mismatch.txt"),  "Version A content here",   T1)
    write_text(os.path.join(src_b, "missing.txt"),   "Only in source",           T1)
    write_text(os.path.join(src_b, "mixed.txt"),     "Mixed content source",     T1)
    write_file(os.path.join(src_b, "contract.docx"), make_docx(),                T1)

    # Target Sub B
    tgt_b = os.path.join(base, "target/Sub B")
    write_text(os.path.join(tgt_b, "exact.txt"),     "Exact match content",      T1)
    write_text(os.path.join(tgt_b, "mismatch.txt"),  "Version B content here",   T2)
    write_text(os.path.join(tgt_b, "mixed.txt"),     "Mixed content source",     T1)
    write_empty(os.path.join(tgt_b, "zero size file.txt"),                        T1)
    write_file(os.path.join(tgt_b, "contract.docx"), make_docx(),                T1)


def build_scenario3(base: str):
    """
    Scenario 3 - Empty source.
    Source folder exists but contains no files.
    Target has files of mixed types.
    Expected: 0 matches, 0 missing, 0 mismatches.
    """
    print("  Building scenario3_empty_source...")

    # Source — empty placeholder only
    os.makedirs(os.path.join(base, "source", "empty"), exist_ok=True)

    # Target — mixed file types
    tgt = os.path.join(base, "target")
    write_text(os.path.join(tgt, "exact.txt"),      "Target only content",       T1)
    write_empty(os.path.join(tgt, "zero size file.txt"),                          T1)
    write_file(os.path.join(tgt, "report.xlsx"),    make_xlsx(),                  T1)
    write_file(os.path.join(tgt, "document.docx"),  make_docx(),                  T1)

    tgt_a = os.path.join(base, "target/Sub A")
    write_text(os.path.join(tgt_a, "exact.txt"),    "Target only content",       T1)

    tgt_b = os.path.join(base, "target/Sub B")
    write_text(os.path.join(tgt_b, "exact.txt"),    "Target only content",       T1)


def build_scenario4(base: str):
    """
    Scenario 4 - Empty target.
    Source has files of mixed types, target folder is empty.
    Expected: all source files missing, 0 matches.
    """
    print("  Building scenario4_empty_target...")

    # Source — mixed file types
    src = os.path.join(base, "source")
    write_text(os.path.join(src, "exact.txt"),      "Source only content",       T1)
    write_empty(os.path.join(src, "zero size file.txt"),                          T1)
    write_file(os.path.join(src, "report.xlsx"),    make_xlsx(),                  T1)
    write_file(os.path.join(src, "document.docx"),  make_docx(),                  T1)

    src_a = os.path.join(base, "source/Sub A")
    write_text(os.path.join(src_a, "exact.txt"),    "Source only content",       T1)

    src_b = os.path.join(base, "source/Sub B")
    write_text(os.path.join(src_b, "exact.txt"),    "Source only content",       T1)

    # Target — empty
    os.makedirs(os.path.join(base, "target"), exist_ok=True)


def build_scenario5(base: str):
    """
    Scenario 5 - Deep nested folders (7 levels).
    Mixed file types at the deepest level.
    Expected: all exact matches.
    """
    print("  Building scenario5_deep_nested...")

    deep = os.path.join("sub a", "sub b", "sub c", "sub d", "sub e", "sub f", "sub g")

    for folder in ["source", "target"]:
        root = os.path.join(base, folder, deep)
        write_text(os.path.join(root, "deep_file.txt"),      "Deep nested content",  T1)
        write_empty(os.path.join(root, "zero size file.txt"),                         T1)
        write_file(os.path.join(root, "deep_report.xlsx"),   make_xlsx(),             T1)
        write_file(os.path.join(root, "deep_document.docx"), make_docx(),             T1)
        write_file(os.path.join(root, "deep_summary.pdf"),   make_pdf("Deep"),        T1)


def build_scenario6(base: str):
    """
    Scenario 6 - Special character filenames.
    Includes: dashes, dots, underscores, spaces, long names, temp files, mixed types.
    Also includes a 'corrupted' docx (valid bytes but renamed as corrupted).
    Expected: all exact matches.
    """
    print("  Building scenario6_special_chars...")

    long_name = "long file name" + "a" * 169 + ".txt"
    docx_bytes = make_docx()

    for folder in ["source", "target"]:
        root = os.path.join(base, folder)
        write_text(os.path.join(root, "file-wtih-dashes.txt"),       "Dashes content",       T1)
        write_text(os.path.join(root, "file.with.dots.txt"),         "Dots content",         T1)
        write_text(os.path.join(root, "file_with_underscores.txt"),  "Underscores content",  T1)
        write_text(os.path.join(root, "test file with spaces.txt"),  "Spaces content",       T1)
        write_empty(os.path.join(root, "zero size file.txt"),                                 T1)
        write_empty(os.path.join(root, long_name),                                            T1)
        write_file(os.path.join(root, "Corrupted File.docx"),        docx_bytes,             T1)
        write_file(os.path.join(root, "spreadsheet report.xlsx"),    make_xlsx(),            T1)
        write_file(os.path.join(root, "policy document.pdf"),        make_pdf("Policy"),     T1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

SCENARIOS = [
    ("scenario1_same",          build_scenario1),
    ("scenario2_mixed",         build_scenario2),
    ("scenario3_empty_source",  build_scenario3),
    ("scenario4_empty_target",  build_scenario4),
    ("scenario5_deep_nested",   build_scenario5),
    ("scenario6_special_chars", build_scenario6),
]


def main():
    parser = argparse.ArgumentParser(
        description="Generate smoke test data for SearchDocuments tool."
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete and recreate all scenario folders"
    )
    parser.add_argument(
        "--base",
        default="testdata",
        help="Base directory for test data (default: testdata)"
    )
    parser.add_argument(
        "--scenario",
        choices=[s[0] for s in SCENARIOS],
        help="Build a single scenario only"
    )
    args = parser.parse_args()

    base_dir = args.base

    # Filter to single scenario if requested
    scenarios = SCENARIOS
    if args.scenario:
        scenarios = [(n, fn) for n, fn in SCENARIOS if n == args.scenario]

    print(f"TestData Generator")
    print(f"Base directory: {os.path.abspath(base_dir)}")
    print(f"Scenarios: {len(scenarios)}")
    print()

    for name, builder in scenarios:
        scenario_path = os.path.join(base_dir, name)

        if args.clean and os.path.exists(scenario_path):
            print(f"  Cleaning {name}...")
            shutil.rmtree(scenario_path)

        if os.path.exists(scenario_path) and not args.clean:
            print(f"  Skipping {name} (already exists — use --clean to recreate)")
            continue

        builder(scenario_path)
        print(f"  Done: {scenario_path}")

    print()
    print("All scenarios complete.")
    print()
    print("Run smoke tests with:")
    print("  build_smoketest.cmd")


if __name__ == "__main__":
    main()