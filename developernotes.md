# Search Documents - Developer Notes

## Project Overview
Search Documents is a file reconciliation tool that compares a SOURCE folder 
against a TARGET folder to identify exact matches, mismatches, and missing files.
The tool supports both a GUI interface and a CLI interface.

## Tool Purpose

Search Documents reconciles SOURCE files against TARGET to 
identify and resolve file organization gaps.

### Definitions
- SOURCE: Files that should exist in TARGET, may have 
          different folder structure
- TARGET: Destination being normalized, gold standard 
          for folder structure

### Two-Phase Reconcilation Process
* Phase 1 — Scan: scan_folder() walks both trees, builds dict keyed by filename
* Phase 2 — Compare: compare_engine iterates source files, looks up candidates in target by filename, applies comparison mode logic

### Comparision Modes
* Fast Mode (default): timestamp + size match → exact match
* Hash Mode (--hash): timestamp + size match confirmed by MD5 hash
* Hash Only Mode (--hashonly): skip timestamp entirely, compare by hash only

### Folder Options
* REPORTS.  Location where output files are created.
* SOURCE.  Folder to use as source of comparison.
* TARGET.  Folder to compare source documents against.

### Output Folders
output_dir
  YYYYMMDD_HHMMSS
    comparison.xlsx
    comparison.csv
    comparison.txt
    summary.txt
    diagnostics_dump.json
    reconciliation_YYYYMMDD_HHMMSS.log   ← log always inside timestamped folder
YYYYMMDD_HHMMSS


### Comparision Options
There are three options to compare files with the same name.
* TIMESTAMP.  This is the fastest option, but the lowest accuracy.  
* HASH COMPARE MODE.  Confirm timestamp matches with hash.
* HASH MODE ONLY.  Skips timestamp comparison, compare exclusively using file hash.

#### COMPARISON SUMMARY
| MODE              | ACCURACY | SPEED     |
|-------------------| ---------|-----------|
| TIMESTAMP         | LEAST    | FASTEST   |
| HASH COMPARE ONLY | MODERATE | MODERATE  |
| HASH MODE ONLY    | MOST     | SLOWEST   |

### Find All Files Option
* This options will looks for all locations where a source file exists in the target folder.  
This option is useful to check for duplication files in the TARGET.  

### Cleanup Options
Action options are used to determine how to handle files that match the Comparison criteria.

| MODE                   | ACTION                    | DESCRPTION                                                                    |
|------------------------|---------------------------|-------------------------------------------------------------------------------|
| DRY RUN                | No files deletions        | No deletions, no quarantine                                                   |
| USE QUARANTINE         | Move deletion candidates  | If DRYRUN is OFF, Delete mismatch candidates only (Permanent Deletions)       |
| DELETE EXACT MATCHES   | Delete Matches            | If DRYRUN IS OFF, Delete exact matches only (Permanent Deletions)             |  
| DELETE CANDIDATES      | Delete Mismatched         | If DRYRUN is OFF, Move BOTH exact matches AND candidates to quarantine folder |                    

### Result Actions

| Result      | Meaning                                  | Immediate Action                           | Follow-up Action                           |
|-------------|------------------------------------------|--------------------------------------------|--------------------------------------------|   
| Exact Match | SOURCE file confirmed in TARGET          | Delete SOURCE or move to Quarantine        | Run tool again to verify                   |
| Missing     | SOURCE file not in TARGET                | Manual copy to correct TARGET location"    | Run tool again — should become Exact Match |
| Mismatch    | Same filename different content          | Determine gold standard                    | Update SOURCE or TARGET accordingly        |
| Multi-Match | SOURCE file in multiple TARGET locations | Keep correct location, clean up duplicates | Run tool again to verify                   |
| Mixed       | Some TARGET copies match some don't      | Keep matches, review mismatches            | Resolve mismatches then run again          |

### Recommended Workflow

### Reconciliation Loop
1. Run tool in DRY_RUN mode — review results
2. Copy Missing files to appropriate TARGET location
3. Resolve Mismatches — determine gold standard
4. Run tool with QUARANTINE enabled — move Exact Matches
5. Verify Quarantine contents
6. Run tool again — verify clean results
7. Repeat until SOURCE is empty or all accounted for

### Recommended Workflow

#### Phase 1 - TARGET Cleanup
Run with TARGET as both FolderA and FolderB:
- Identify duplicate files in TARGET
- Resolve same filename different content
- Expected: Missing = 0 always

#### Phase 2 - SOURCE Reconciliation (Dry Run First)
Run with SOURCE as FolderA and TARGET as FolderB:
    --dryrun
- Review all results before making changes
- Identify Missing files for manual copying
- Identify Exact Matches for deletion/quarantine

#### Phase 3 - Execute Reconciliation
Run again with action flags:
    --quarantine --deletematches
- Exact Matches moved to Quarantine
- Verify Quarantine contents before emptying

#### Phase 4 - Verify Clean
Run tool again:
- Missing = 0 ✅
- Exact Matches = 0 ✅  
- SOURCE fully reconciled ✅

#### Phase 5 - File Placement (Future)
AI classification for Missing files:
- Suggests TARGET location based on content/context
- Generates action plan for human review
- Execute approved plan automatically

### Design Principles
- Filename-only matching allows cross-structure comparison
- TARGET folder structure is the gold standard
- SOURCE folder structure is not relevant to matching
- Find All Files enabled by default
- DRY_RUN recommended before any destructive operations
- Quarantine preferred over direct deletion for safety
- All destructive actions require explicit flag enablement
- Reconciliation is iterative — run multiple times until clean
---

## Project Structure
```
<pre>
src/
  cli/cli_main.py          - CLI entry point, argparse, --version flag
  gui/gui_main.py          - Tkinter GUI entry point
  engine/compare_engine.py - Core reconciliation logic
  orchestrator.py          - Coordinates engine + writers
  config.py                - Runtime flags (singleton pattern)
  utilities/
    logging_setup.py       - init_logging, diag
    output.py              - create_timestamped_folder
    path_utils.py          - get_version, get_version_info, resource_path
    safe_delete.py         - safe_delete, move_to_quarantine, handle_delete
    scan_folder.py         - scan_folder, dump_scan_results
  writers/
    excel_writer.py
    csv_writer.py
    text_writer.py
    summary_writer.py
    write_all_reports.py   - Unified wrapper, error isolation per writer
  assets/
    Search-documents.ico     # Application icon
│   Search-documents.png     # Splash screen image
tools/
  create_testdata.py       - Generates all 6 smoke test scenarios
testdata/
  scenario1_same/          - Identical files, mixed types
  scenario2_mixed/         - Mixed results
  scenario3_empty_source/  - Empty source folder
  scenario4_empty_target/  - Empty target folder
  scenario5_deep_nested/   - 7 levels deep
  scenario6_special_chars/ - Special filenames, mixed types
├── build.cmd                    # Windows build script
├── conftest.py                  # pytest configuration
├── DEVELOPER_NOTES.md           # This file
├── pyproject.toml               # Package configuration
├── pytest.ini                   # pytest settings
└── README.md                    # User documentation
</pre>
```
## Smoke Test Data Expected Results
| Scenario        | Src Files | Tgt Files | Matches | Mismatches | Missing | Multi | Mixed |
|-----------------|-----------|-----------|---------|------------|---------|-------|-------|
| 1-Identical     | 9         | 9         | 9       | 0          | 0       | 3     | 0     |
| 2-Mixed         | 18        | 17        | 11      | 1          | 1       | 4     | 1     |
| 3-Empty Source  | 0         | 6         | 0       | 0          | 0       | 0     | 0     |
| 4-Empty Target  | 6         | 0         | 0       | 2          | 2       | 0     | 0     |
| 5-Deep Nested   | 5         | 5         | 5       | 0          | 0       | 0     | 0     |
| 6=Special Chars | 9         | 9         | 9       | 0          | 0       | 0     | 0     |
---

## Development Environment Setup

### Prerequisites
- Python 3.14+
- Windows 10/11 (primary development platform)
- Git
- Notepad++ or PyCharm (recommended IDE)

### Initial Setup (New Machine)
```bash
# Step 1 - Clone repository (once GitHub is configured)
git clone <repository_url>
cd searchdocuments

# Step 2 - Create virtual environment
python -m venv venv

# Step 3 - Activate virtual environment
venv\Scripts\activate

# Step 4 - Install dependencies
pip install -r requirements.txt

# Step 5 - Install project in editable mode
pip install -e .

# Step 6 - Verify setup
pytest -v
```

### Daily Startup
```bash
cd D:\dev\Projects\searchdocuments
venv\Scripts\activate
```
You will know venv is active when you see `(venv)` in your prompt:
```
(venv) D:\dev\Projects\searchdocuments>
```

---

## Dependencies

### Runtime Dependencies
| Package  | Version  | Purpose                 |
|----------|----------|-------------------------|
| openpyxl | latest   | Excel report generation |
| tkinter  | built-in | GUI framework           |

### Development Dependencies
| Package     | Version | Purpose                      |
|-------------|---------|------------------------------|
| pytest      | latest  | Test runner                  |
| pytest-cov  | latest  | Code coverage reporting      |
| pytest-ruff | latest  | Ruff integration with pytest |
| ruff        | latest  | Code quality and linting     |

### Installing All Dependencies
```bash
pip install -r requirements.txt
```

### Updating requirements.txt
```bash
pip freeze > requirements.txt
```

---

## Running the Application

### GUI Mode
```bash
# From command line (development)
python src/gui/gui_main.py

# Built executable
dist\Search-documents_GUI.exe
```

### CLI Mode
```bash
# Basic usage
python src/cli/cli_main.py folderA folderB -o output_dir

# With options
python src/cli/cli_main.py folderA folderB -o output_dir --hash --dryrun --diag

# Built executable
dist\Search-documents_CLI.exe folderA folderB -o output_dir
```

### CLI Arguments
| Argument             | Type     | Description                    |
|----------------------|----------|--------------------------------|
| `folderA`            | required | Source folder path             |
| `folderB`            | required | Target folder path             |
| `-o, --output`       | required | Output directory for reports   |
| `--hash`             | flag     | Enable hash comparison mode    |
| `--hashonly`         | flag     | Enable hash-only mode          |
| `--findall`          | flag     | Find all locations in Folder B |
| `--dryrun`           | flag     | Dry run, no changes made       |
| `--deletematches`    | flag     | Delete exact matches           |
| `--deletecandidates` | flag     | Delete mismatch candidates     |
| `--quarantine`       | flag     | Use quarantine folder          |
| `--diag`             | flag     | Enable diagnostic output       |
| `--version`          | flag     | Show version number            |

---

## Configuration Flags (config.py)

| Flag                      | Default | Description                  |
|---------------------------|---------|------------------------------|
| `DIAGNOSTIC_MODE`         | False   | Master diagnostic switch     |
| `DIAG_SCAN`               | False   | Scan diagnostic output       |
| `DIAG_COMPARE`            | False   | Compare diagnostic output    |
| `DIAG_WRITERS`            | False   | Writers diagnostic output    |
| `FIND_ALL_LOCATIONS_MODE` | False   | Find all file locations      |
| `TIMESTAMPED_OUTPUT`      | True    | Timestamped output folders   |
| `SILENT_MODE`             | False   | Suppress console output      |
| `HASH_COMPARE_MODE`       | False   | Timestamp+size then hash     |
| `HASH_ONLY_MODE`          | False   | Hash only comparison         |
| `DRY_RUN`                 | False   | No changes made              |
| `USE_QUARANTINE`          | False   | Quarantine instead of delete |
| `DELETE_EXACT_MATCHES`    | False   | Delete exact matches         |
| `DELETE_CANDIDATES`       | False   | Delete mismatch candidates   |

---

## Testing

### Run All Tests
```bash
pytest -v
```

### Run Single Test File
```bash
pytest tests/test_compare_engine.py -v
```

### Run Single Test
```bash
pytest tests/test_compare_engine.py::test_name -v -s
```

### Debug Failing Test
```bash
# Full debug output with local variables and preserved temp files
pytest tests/test_name.py::test_name -v -s -l --basetemp=D:\dev\Projects\searchdocuments\test_debug
```

### Run with Coverage Report
```bash
pytest -v --cov=src --cov-report=term-missing
```

### Debug Switch Reference
| Switch       | Purpose                                |
|--------------|----------------------------------------|
| `-v`         | Verbose — shows each test name         |
| `-s`         | Shows print() output in console        |
| `-l`         | Shows local variable values on failure |
| `--basetemp` | Saves temp files to browsable folder   |

### Current Coverage Status
| File                   | Coverage       |
|------------------------|----------------|
| `config.py`            | 100%           |
| `compare_engine.py`    | 100%           |
| `logging_setup.py`     | 100%           |
| `orchestrator.py`      | 100%           |
| `output.py`            | 100%           |
| `path_utils.py`        | 100%           |
| `safe_delete.py`       | 100%           |
| `scan_folder.py`       | 100%           |
| `csv_writer.py`        | 100%           |
| `excel_writer.py`      | 100%           |
| `summary_writer.py`    | 100%           |
| `text_writer.py`       | 100%           |
| `write_all_reports.py` | 100%           |
| `cli_main.py`          | 100%           |
| `gui_main.py`          | 0% (by design) |
| **Total**              | **78%**        |

---
Current Coverage Status
---
## Code Quality

### Run Ruff Check
```bash
# Check source code
ruff check src/

# Check tests too
ruff check src/ tests/

# Auto fix issues
ruff check src/ --fix
```
## Testing Conventions
### Specific Topics Relevant to Unit Testing
| Topic        | What Used for                     | Reference                |
|--------------|-----------------------------------|--------------------------|
| MagicMock    | Status/progress callbacks         | unittest.mock docs       |
| patch        | Replacing writers, reconciliation | Real Python mock article |
| side_effect  | Simulating exceptions             | unittest.mock docs       |
| return_value | Controlling mock output           | unittest.mock docs       |
| monkeypatch  | sys.argv, config flags            | pytest docs              |
| tmp_path     | Temporary file creation           | pytest docs              |
| caplog       | Log message capture               | pytest docs              |
 | capsys       | stdout/stderr capture             | pytest docs              |

### Key Concepts to Focus On:
MagicMock vs Mock:

MagicMock supports magic methods like __len__, __str__
### Use MagicMock by default unless you have a specific reason not to
```bash
status_mock = MagicMock()
status_mock("some message")
assert status_mock.called
assert status_mock.call_count == 1
print(status_mock.call_args_list)  # see all calls
patch as context manager vs decorator:
```
### patch as context manager vs decorator:
#### Context manager - what you use most
```bash
with patch("src.writers.write_all_reports.build_summary",
           return_value=None) as mock_summary:
    write_all_reports(...)
    assert mock_summary.called
# Decorator - alternative approach
@patch("src.writers.write_all_reports.build_summary")
def test_something(mock_summary):
    mock_summary.return_value = None
    write_all_reports(...)
````

### side_effect for exceptions:
``` bash
# Force an exception
with patch("src.writers.write_all_reports.build_summary",
           side_effect=Exception("failed")):
    write_all_reports(...)  # exception is raised inside
# side_effect with a function

def custom_behavior(*args, **kwargs):
    if args[0] == "bad_input":
        raise ValueError("bad!")
    return "ok"

with patch("some.function", side_effect=custom_behavior):
    ...
```

### monkeypatch vs patch:
``` bash
# monkeypatch - pytest native, auto resets after test
def test_something(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["cli", "folderA", "folderB", "-o", "out"])
    monkeypatch.setattr(config, "DRY_RUN", True)

# patch - unittest.mock, use as context manager or decorator
with patch("src.config.DRY_RUN", True):
    ...
```

### call_args_list — inspecting mock calls:
``` bash
status_mock = MagicMock()
status_mock("first message")
status_mock("second message")

# Get all calls
calls = [c[0][0] for c in status_mock.call_args_list]
# calls = ["first message", "second message"]

# Check last call
last_call = status_mock.call_args_list[-1][0][0]
assert "Reports written to" in last_call

# Check any call
assert any("ERROR" in c.upper() for c in calls)
```

### Recommended Reading Order:

Real Python pytest guide — understand fixtures first
Real Python mock article — understand patch and MagicMock
Official unittest.mock docs — reference when you need details
pytest fixtures docs — deep dive into tmp_path, monkeypatch, caplog

### Patterns Used in Your Codebase — Quick Reference:
#### Pattern 1 - Mock callback and verify calls
status_mock = MagicMock()
write_all_reports(..., status_callback=status_mock)
assert status_mock.called
calls = "[c[0][0]" for c in status_mock.call_args_list]
assert any("ERROR" in c.upper() for c in calls)

#### Pattern 2 - Patch writer to isolate test
with patch(PATCH_EXCEL, return_value=None) as mock_excel:
    write_all_reports(...)
assert mock_excel.called

#### Pattern 3 - Force exception to test error handling
with patch(PATCH_EXCEL, side_effect=Exception("failed")):
    write_all_reports(...)  # should not raise

#### Pattern 4 - Monkeypatch sys.argv for CLI tests
monkeypatch.setattr(sys, "argv", ["cli", "folderA", "folderB", "-o", "out"])
run_cli()

#### Pattern 5 - tmp_path for file operations
def test_something(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    assert test_file.exists()

#### Pattern 6 - caplog for log message capture
def test_logging(caplog):
    with caplog.at_level(logging.INFO):
        some_function()
    assert "expected message" in caplog.text

### Error Message Assertions
- Use precise text matching for user facing messages that must be exact
- Use flexible pattern matching (e.g. "ERROR" in c.upper()) for internal error messages
- Avoid asserting diag() message text in tests
- Avoid asserting logging.debug() message text in tests

### Updating Output Format
When changing any user facing output text such as report titles,
status messages or summary labels always run:

    findstr /s /n "old text" tests\*.py

to find all test assertions that reference the old text before
committing. Stale assertions will pass in isolation but fail
in the full suite due to test ordering.

### General Principles
- Test behavior not implementation
- Test what the user or caller experiences
- Avoid brittle dependencies on internal message wording

---

### Prerequisites
- PyInstaller installed in venv
- All tests passing
- Ruff check clean

### Build Steps (automated in build.cmd)
1. 'Activate venv'
2. 'Run ruff check src/ tests/' — stops if errors found
3. 'Run pytest -v' — stops if tests fail
4. 'Clean dist/ and build/ folders'
5. 'Post build some tests (54 checks x 6 scenarios'
6. 'Build CLI executable'
7. 'Build GUI executable'

### Build Output
```
dist\
    Search-documents_CLI.exe
    Search-documents_GUI.exe
```

### Linux Build Note
```bash
# Linux --add-data uses colon separator instead of semicolon
--add-data "src/utilities:utilities"
```

---

## Git Workflow

### Daily Workflow
```bash
# Check status
git status

# Stage all changes
git add .

# Stage specific file
git add src/module.py

# Commit with descriptive message
git commit -m "Brief description of changes"

# Push to remote (once GitHub configured)
git push


```

### Useful Git Commands
```bash
# Check all tracked files
git ls-files

# Check tracked files in specific folder
git ls-files tests/
git ls-files src/

# Check what is being ignored
git check-ignore -v src/*
git check-ignore -v tests/*

# View recent commits
git log --oneline -5

# Check current branch
git branch
# Confirm reports excluded
git check-ignore -v testdata/reports/
# Expected: .gitignore:49:testdata/reports/   testdata/reports/  ✅

# Confirm scenario folders NOT excluded
git check-ignore -v testdata/scenario1_same/
# Expected: no output  ✅

# Confirm test files NOT excluded
git check-ignore -v testdata/scenario1_same/source/
# Expected: no output  ✅

# Confirm debug excluded
git check-ignore -v testdata/debug/
# Expected: .gitignore:xx:testdata/debug/   testdata/debug/  ✅
```

### Git Ignore Key Rules
- `venv/` — never commit virtual environment
- `*.log` — never commit log files
- `*.xlsx, *.csv, *.txt` — never commit generated reports
- `__pycache__/` — never commit compiled Python
- `dist/, build/` — never commit build artifacts
- `test_debug/` — never commit debug output
- `test_debug/` — never commit debug output
- '# Python
  - '' __pycache__/
  - '*.pyc
  - '*.pyo
  - '*.pyd
  - '*.egg-info/

- '#Virtual environments
  - 'venv/
  - '.env/
  - '.venv/
  - 'env/

- '# PyInstaller build artifacts
  - 'build/
  - 'dist/
  - '*.spec

- '# Logs
    - '*.log
    - '*.tmp
- '*.bak
- '*.swp
- '~*.*
- '*~

- '# Quarantine folder
  - 'Quarantine/

- '# IDE files
  - '.vscode/
  - '.idea/

- '# do not checkin these files
  - '*.tmp
  - '*.bak
  - '*.swp
  - '~*.*
  - '*~

- '# Generated reports
- '# Test output
  - 'testdata/reports/
  - 'testdata/debug/


- '# JSON exception for app version
  - '*.json
  - '!src/app_version.json

-# Executables and installers
  - '*.exe
  - '*.msi
  - '*.dll
  - '*.manifest

-#ignore OS  Editor Junk
-# macOS
    - '.DS_Store

'# Windows
    - 'Thumbs.db
    - 'desktop.ini

-#Python specific
    - 'venv/
  - '__pycache__/
  - '.pytest_cache/dir

---

## Version Management

### version_info.txt Location
```
src/version_info.txt
```

### version_info.txt Format
```json
{
    "version": "1.0.0",
    "build": "20260301",
    "author": "Your Name",
    "description": "Search Documents - File Reconciliation Tool",
    "release": "Production"
}
```

### Updating Version
1. Edit `src/app_version.json`
2. Update build date to today
3. Run `pytest -v` to confirm tests pass
4. Run `build.cmd` to create new executables
5. Commit with version tag:
```bash
git add .
git commit -m "Release v1.0.0"
```

---

## Known Issues and Limitations

### Open Issues

### Design Decisions
- `gui_main.py` excluded from unit test coverage by design
- `pragma: no cover` used on unreachable hash-only branch in compare_engine.py
- SOURCE is assumed to be equal to or a subset of TARGET

### Future Enhancements
- Target-only files silently ignored (no target only report category)
- GitHub repository setup
- File placement automation with AI classification
- Action plan report generation with execute mode
- Strict mode for exact mirror validation
- Linux build support

---

## Troubleshooting

### venv Not Activating
```bash
# Confirm you are in the right directory
cd D:\dev\Projects\searchdocuments

# Activate
venv\Scripts\activate

# Confirm activation - should see (venv) in prompt
(venv) D:\dev\Projects\searchdocuments>
```

### Tests Not Collecting
```bash
# Run pytest directly on the file
pytest tests/test_name.py -v

# Check if file is tracked by git
git ls-files tests/

# Confirm file exists
dir tests\test_name.py
```

### Import Errors in Tests
```bash
# Confirm conftest.py has both paths
# conftest.py should contain:
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))
```

### Build Fails
```bash
# Step 1 - confirm ruff is clean
ruff check src/

# Step 2 - confirm tests pass
pytest -v

# Step 3 - Clean previous builds artifacts

# Step 4 - Post build smoke tests (54 checks x 6 scenarios)

# Step 5 - Build CLI executable

# Step 6 - Build GUI executable
```

## Logging Best Practices
---
### Logging Conventions
| Method                | When to Use                                                      |
|-----------------------|------------------------------------------------------------------|
| `logging.info()`      | Normal operational messages                                      |
| `logging.warning()`   | Unexpected but recoverable situations                            |
| `logging.error()`     | Errors and exceptions                                            |
| `logging.exception()` | Errors with full stack trace                                     |
| `logging.debug()`     | detailed trace, diag mode only                                   |
| `diag()`              | Detailed debug info when DIAGNOSTIC_MODE=True                    |
| `print()`             | User facing CLI output only                                      |
| `Log fie`             | always created inside timestamped output folder                  | 
| `GUI Logging`         | Loggings starts only when Run is clicked and output folder known |

### Files Audit Logging Summary
| File              | Logging              | diag                                 | print        |
|-------------------|----------------------|--------------------------------------|--------------|
| gui_main.py       | init, errors         | config state, run details            | never        |
| cli_main.py       | init, errors         | config state, run details            | summary only |
| compare_engine.py | none needed          | scan, compare results, match details | never        |
| orchestrator.py   | start/end milestones | entry point                          | never        |
| writers/          | errors only          | checkpoints, completion              | never        |
| utilities/        | errors only          | internal state                       | never        |
| config.py         | none needed          | none needed                          | never        |


```bash
logging.xxx() — Operational Messages
Label  
Info
Use for events that matter in production and should always appear in the log file regardless of diagnostic settings
# logging.info() — normal successful operations
logging.info(f"Logging initialized: {log_path}")
logging.info(f"GUI Log file created: {log_path}")
logging.info(f"Reports written to: {output_dir}")

# logging.warning() — unexpected but recoverable
logging.warning(f"Output dir not specified, using cwd: {os.getcwd()}")
logging.warning(f"File skipped, path invalid: {path}")

# logging.error() — something failed but app continues
logging.error(f"Failed to write CSV report: {e}")
logging.error(f"GUI ERROR: {e}")
logging.error(f"CLI ERROR: {e}")

# logging.exception() — error WITH full stack trace
# Use ONLY inside except blocks when stack trace is valuable
try:
    run_reconciliation(...)
except Exception as e:
    logging.exception("Unexpected error in reconciliation")

# logging.critical() — app cannot continue
logging.critical("Cannot create output directory, aborting")
```
```bash
diag() — Developer Debug Messages
Use for detailed internal state that developers need when diagnosing problems. Only appears in log file when DIAGNOSTIC_MODE=True.
```
```bash
print() — User Facing Output Only
Use sparingly and only for output that is intentionally displayed to the user in CLI mode. Never use inside business logic, utilities, or writers.
```
---
## Contact and Support
- Project: Search Documents
- Developer: Ray Rials
- Last Updated: March 2026