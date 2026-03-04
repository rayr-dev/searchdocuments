# Search Documents - Developer Notes

## Project Overview
Search Documents is a file reconciliation tool that compares a SOURCE folder 
against a TARGET folder to identify exact matches, mismatches, and missing files.
The tool supports both a GUI interface and a CLI interface.

---

## Project Structure
```
searchdocuments/
├── src/
│   ├── cli/
│   │   └── cli_main.py          # Command line interface
│   ├── engine/
│   │   └── compare_engine.py    # Core comparison logic
│   ├── gui/
│   │   └── gui_main.py          # Tkinter GUI interface
│   ├── utilities/
│   │   ├── logging_setup.py     # Logging initialization
│   │   ├── output.py            # Output directory creation
│   │   ├── path_utils.py        # Path helpers, version info
│   │   ├── safe_delete.py       # Safe delete and quarantine
│   │   └── scan_folder.py       # Folder scanning
│   ├── writers/
│   │   ├── csv_writer.py        # CSV report writer
│   │   ├── excel_writer.py      # Excel report writer
│   │   ├── summary_writer.py    # Summary report writer
│   │   ├── text_writer.py       # Text report writer
│   │   └── write_all_reports.py # Unified report wrapper
│   ├── config.py                # Global configuration flags
│   ├── orchestrator.py          # Run reconciliation entry point
│   └── version_info.txt         # Application version info (JSON)
├── tests/
│   ├── test_cli_main.py
│   ├── test_compare_engine.py
│   ├── test_config.py
│   ├── test_csv_writer.py
│   ├── test_excel_writer.py
│   ├── test_logging_setup.py
│   ├── test_orchestrator.py
│   ├── test_path_utils.py
│   ├── test_safe_delete.py
│   ├── test_scan_folder.py
│   ├── test_summary_writer.py
│   ├── test_text_writer.py
│   └── test_write_all_reports.py
├── assets/
│   ├── Search-documents.ico     # Application icon
│   └── Search-documents.png     # Splash screen image
├── testdata/
│   ├── source/                  # Test source folder
│   ├── target/                  # Test target folder
│   └── reports/                 # Test output folder
├── .gitignore
├── build.cmd                    # Windows build script
├── conftest.py                  # pytest configuration
├── DEVELOPER_NOTES.md           # This file
├── pyproject.toml               # Package configuration
├── pytest.ini                   # pytest settings
└── README.md                    # User documentation
```

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
| Package | Version | Purpose |
|---------|---------|---------|
| openpyxl | latest | Excel report generation |
| tkinter | built-in | GUI framework |

### Development Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| pytest | latest | Test runner |
| pytest-cov | latest | Code coverage reporting |
| pytest-ruff | latest | Ruff integration with pytest |
| ruff | latest | Code quality and linting |

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
| Argument | Type | Description |
|----------|------|-------------|
| `folderA` | required | Source folder path |
| `folderB` | required | Target folder path |
| `-o, --output` | required | Output directory for reports |
| `--hash` | flag | Enable hash comparison mode |
| `--hashonly` | flag | Enable hash-only mode |
| `--findall` | flag | Find all locations in Folder B |
| `--dryrun` | flag | Dry run, no changes made |
| `--deletematches` | flag | Delete exact matches |
| `--deletecandidates` | flag | Delete mismatch candidates |
| `--quarantine` | flag | Use quarantine folder |
| `--diag` | flag | Enable diagnostic output |
| `--version` | flag | Show version number |

---

## Configuration Flags (config.py)

| Flag | Default | Description |
|------|---------|-------------|
| `DIAGNOSTIC_MODE` | False | Master diagnostic switch |
| `DIAG_SCAN` | False | Scan diagnostic output |
| `DIAG_COMPARE` | False | Compare diagnostic output |
| `DIAG_WRITERS` | False | Writers diagnostic output |
| `FIND_ALL_LOCATIONS_MODE` | False | Find all file locations |
| `TIMESTAMPED_OUTPUT` | True | Timestamped output folders |
| `SILENT_MODE` | False | Suppress console output |
| `HASH_COMPARE_MODE` | False | Timestamp+size then hash |
| `HASH_ONLY_MODE` | False | Hash only comparison |
| `DRY_RUN` | False | No changes made |
| `USE_QUARANTINE` | False | Quarantine instead of delete |
| `DELETE_EXACT_MATCHES` | False | Delete exact matches |
| `DELETE_CANDIDATES` | False | Delete mismatch candidates |

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
| Switch | Purpose |
|--------|---------|
| `-v` | Verbose — shows each test name |
| `-s` | Shows print() output in console |
| `-l` | Shows local variable values on failure |
| `--basetemp` | Saves temp files to browsable folder |

### Current Coverage Status
| File | Coverage |
|------|----------|
| `config.py` | 100% |
| `compare_engine.py` | 100% |
| `logging_setup.py` | 100% |
| `orchestrator.py` | 100% |
| `output.py` | 100% |
| `path_utils.py` | 100% |
| `safe_delete.py` | 100% |
| `scan_folder.py` | 100% |
| `csv_writer.py` | 100% |
| `excel_writer.py` | 100% |
| `summary_writer.py` | 100% |
| `text_writer.py` | 100% |
| `write_all_reports.py` | 100% |
| `cli_main.py` | 100% |
| `gui_main.py` | 0% (by design) |
| **Total** | **77%** |

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

### Error Message Assertions
- Use precise text matching for user facing messages that must be exact
- Use flexible pattern matching (e.g. "ERROR" in c.upper()) for internal error messages
- Avoid asserting diag() message text in tests
- Avoid asserting logging.debug() message text in tests

### General Principles
- Test behavior not implementation
- Test what the user or caller experiences
- Avoid brittle dependencies on internal message wording

## Test Data
## Test Data Structure
Use CMD>tree to generate markdown graphic

### Same Data
### Folder Structure
### Expected Summary Report

### Different Data
### Folder Structure
### Expected Summary Report

### No files in targer
### Folder Structure
### Expected Summary Report


---

## Build Process

### Prerequisites
- PyInstaller installed in venv
- All tests passing
- Ruff check clean

### Run Build
```bash
build.cmd
```

### Build Steps (automated in build.cmd)
1. Activate venv
2. Run ruff check — stops if errors found
3. Run pytest — stops if tests fail
4. Clean dist/ and build/ folders
5. Build CLI executable
6. Build GUI executable

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
1. About box version display — under investigation
2. GUI summary output differs from summary.txt — under investigation
3. Files in TARGET but not in SOURCE — use case review needed

### Design Decisions
- `gui_main.py` excluded from unit test coverage by design
- `pragma: no cover` used on unreachable hash-only branch in compare_engine.py
- SOURCE is assumed to be equal to or a subset of TARGET

### Future Enhancements
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

# Step 3 - confirm venv is active
venv\Scripts\activate

# Step 4 - confirm PyInstaller is installed
pyinstaller --version
```

## Logging Best Practices
---
### Logging Conventions
| Method | When to Use |
|--------|-------------|
| `logging.info()` | Normal operational messages |
| `logging.warning()` | Unexpected but recoverable situations |
| `logging.error()` | Something failed but app continues |
| `logging.exception()` | Errors with full stack trace |
| `diag()` | Detailed debug info when DIAGNOSTIC_MODE=True |
| `print()` | User facing CLI output only |

### Files Audit Logging Summary
| File        | Logging | diag | print|
|-------------| ------- | ---- | -----|
| gui_main.py | init, errors | config state, run details | never |
| cli_main.py | init, errors | config state, run details | summary only |
| compare_engine.py | none needed | scan, compare results, match details | never |
| orchestrator.py | start/end milestones | entry point | never |
| writers/ | errors only | checkpoints, completion | never |
| utilities/ | errors only | internal state | never |
| config.py | none needed | none needed | never|


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