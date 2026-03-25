# Contributing to Search Documents

Thank you for your interest in contributing!

## Development Setup
```bash
git clone https://github.com/rayr-dev/searchdocuments.git
cd searchdocuments
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Code Standards

All contributions must pass the following before submitting a PR:

### Linting
```bash
ruff check src/ tests/
```

### Tests
```bash
pytest -v
```

### Smoke Tests
```bash
post_build_test.cmd
```

**Requirements:**
- 100% test coverage on all non-GUI source files
- All 308 tests passing
- All 72 smoke test checks passing
- No ruff violations

## Project Structure
```
src/engine/          # Core comparison logic — compare_engine.py
src/writers/         # Report writers — Excel, CSV, Text, Summary
src/utilities/       # Shared utilities — logging, path, scan, delete
src/cli/             # Command line interface
src/gui/             # Tkinter GUI
tests/               # Pytest test suite
tools/               # Test data generator
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Run ruff, pytest, and smoke tests — all must pass
5. Commit with a clear message describing what and why
6. Push and open a Pull Request against `main`

## Reporting Issues

Submit issues at: https://github.com/rayr-dev/searchdocuments/issues

Please include:
- What you expected to happen
- What actually happened
- Steps to reproduce
- OS and Python version