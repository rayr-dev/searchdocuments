# Search Documents — File Reconciliation Tool

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Tests](https://img.shields.io/badge/tests-308%20passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-100%25%20non--GUI-brightgreen)
![CI](https://github.com/rayr-dev/searchdocuments/actions/workflows/ci.yml/badge.svg)

A fast, reliable utility for comparing two folders of documents and reconciling their contents. Produces Excel, CSV, and text reports and can optionally delete or quarantine duplicate or outdated files.

---

## What It Does

The tool compares a **Source folder** (Folder A) against a **Target folder** (Folder B).

| Result | Meaning | Required Action |
|---|---|---|
| Exact Match | Source file exists correctly in Target | Candidate to remove from Source |
| Missing | Source file not found anywhere in Target | Candidate to move to correct Target location |
| Mismatch | Same filename, different content | Reconcile gold standard file, remove others |
| Multi-Match | Source file found in multiple Target locations | Clean up multiple copies in Target |
| Mixed | Some Target copies match, some don't | Clean up duplicates and mixed content |
| Target Only | File exists in Target but not in Source | Review for stale or rogue files |

### Source vs Target

- **Target** is the gold standard for file system structure — the destination being normalized over time. It may have files in wrong locations, duplicate copies, or missing files from Source.
- **Source** contains files that should exist in Target. It may have a different folder structure than Target and represents files that need to be reconciled.

---

## Quick Start

### Prerequisites
- Python 3.10 or later
- Windows 10 or later (Linux support planned)

### Clone and Install
```bash
git clone https://github.com/rayr-dev/searchdocuments.git
cd searchdocuments
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Run the GUI
```bash
python src\gui\gui_main.py
```

### Run the CLI
```bash
python src\cli\cli_main.py <source_folder> <target_folder> [options]
```

---

## CLI Options
```
python src\cli\cli_main.py <source> <target> [options]
```

| Option | Meaning |
|---|---|
| `--hashonly` | Use SHA-256 hash only (ignores timestamp and size) |
| `--findall` | Find all locations of a file in Target |
| `--delete-matches` | Delete exact matches from Source |
| `--delete-candidates` | Delete mismatch candidates from Source |
| `--no-quarantine` | Delete files instead of quarantining them |
| `--no-dry-run` | Execute deletions (default is dry-run) |
| `--silent` | Suppress all console output |
| `--timestamped-output` | Create a timestamped output subfolder |

---

## Output Files

After running, the tool creates three report files in the output folder:

### Excel Report (`comparison.xlsx`)

| Color | Meaning |
|---|---|
| Green | Exact match |
| Yellow | Mismatch |
| Red | Missing in Target |
| Orange | Target Only (exists in Target, not in Source) |

Each row shows: Status, Filename, Path A, Timestamp A, Path B, Timestamp B, Action taken.

### CSV Report (`comparison.csv`)
Same data as Excel, suitable for importing into other systems.

### Text Report (`comparison.txt`)
A readable summary grouped into: Exact Matches, Mismatches, Missing Files, Target Only.

### Summary Report (`summary.txt`)
```
=============== RECONCILIATION REPORT ===============
Source Statistics:
   Total Files in Source:      X
   Total Files in Target:      X
   Unique filenames in Source: X
   Unique filenames in Target: X

Reconciliation Results:
   Total Exact Matches:        X
   Total Mismatches:           X
   Total Missing Files:        X
   Total Target Only Files:    X

   Multi-Match Cases:          X
   Mixed Match/Mismatch:       X

   Files Deleted:              X
   Files Quarantined:          X
=====================================================
```

---

## Comparison Modes

| Mode | How It Works | Speed |
|---|---|---|
| Fast (default) | Timestamp + size | Fastest |
| Hash Compare | Timestamp + size + SHA-256 | Slower |
| Hash Only (`--hashonly`) | SHA-256 only | Slower |

> **Note:** Fast Mode cannot detect corrupted files with identical size and timestamp. Use Hash Only Mode when content integrity is critical.

---

## Deletion and Quarantine Options

| Mode | Behaviour |
|---|---|
| Dry-Run (default) | No files changed — actions logged only |
| Quarantine (default when deleting) | Files moved to a `quarantine/` subfolder |
| Delete | Files permanently removed |

Deletion applies to **Source** files:
- `--delete-matches` removes Source files that match exactly in Target
- `--delete-candidates` removes Source mismatch candidates

All actions are logged to `file_compare_deletions.log`.

---

## Deletion Log

All deletion and quarantine actions are recorded with:
- Timestamp
- Action (deleted, quarantined, dry-run)
- File path
- Reason (exact match, mismatch, duplicate)

---

## Project Structure
```
searchdocuments/
├── src/
│   ├── cli/            # Command line interface
│   ├── engine/         # Core comparison engine
│   ├── gui/            # Tkinter GUI
│   ├── utilities/      # Logging, path utils, safe delete, scan
│   ├── writers/        # Excel, CSV, text, summary report writers
│   └── config.py       # Feature flags and configuration
├── tests/              # Pytest test suite (308 tests)
├── tools/
│   └── create_testdata.py   # Generates all smoke test scenarios
├── post_build_test.cmd      # 72-check smoke test suite
├── requirements.txt
└── README.md
```

---

## Development

### Running Tests
```bash
pytest -v
```

### Running Smoke Tests
```bash
# Regenerates all test data and runs 72 checks across 7 scenarios
post_build_test.cmd
```

### Test Scenarios

| Scenario | Description |
|---|---|
| 1 — Identical Files | All files match exactly including duplicates |
| 2 — Mixed Results | Mix of matches, mismatches, and missing files |
| 3 — Empty Source | Source folder is empty |
| 4 — Empty Target | Target folder is empty |
| 5 — Deep Nested | Files nested 7 levels deep |
| 6 — Special Characters | Filenames with dashes, dots, spaces, long names |
| 7 — Corrupted Files | Identical size/name but different bytes — proves Fast Mode limitation |

### Building the EXE
```bash
build.cmd
```
Produces a standalone Windows EXE in `dist/`. No Python installation required to run.

---

## Troubleshooting

**Access Denied errors** — The file may be locked or require admin permissions.

**Excel report won't open** — Ensure Excel is installed and not already running in safe mode.

**Quarantine folder not created** — Check that the tool has write permission to the output directory.

---

## System Requirements

- Windows 10 or later
- Python 3.10+ (for running from source)
- No admin rights needed unless deleting protected files

---

## Support

For questions, enhancements, or bug reports, submit an issue at:
https://github.com/rayr-dev/searchdocuments/issues