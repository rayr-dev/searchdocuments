REM rmdir /s /q dist
REM rmdir /s /q build
REM pyinstaller --clean --noconfirm --name Search-documents_CLI --console --icon assets/Search-documents.ico --paths src --add-data "src\utilities;utilities" --add-data "src\version_info.txt;." --distpath dist --workpath build src/cli/cli_main.py

REM pyinstaller --clean --noconfirm --name Search-documents_GUI --windowed --icon assets/Search-documents.ico --splash assets/Search-documents.png --paths src --add-data "src\utilities;utilities" --add-data "src\version_info.txt;." --distpath dist --workpath build src/gui/gui_main.py
REM For Linux builds src/utilities:utiliites

@echo off
setlocal enabledelayedexpansion

echo ================================================
echo  Search Documents - Build Process
echo ================================================
echo.

REM ------------------------------------------------
REM Step 1: Code Quality Check
REM ------------------------------------------------
echo [1/5] Running Ruff code quality check...
call venv\Scripts\activate
ruff check src/
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo FAILED: Ruff check failed.
    echo Fix code quality issues before building.
    echo Run: ruff check src/ --fix
    exit /b 1
)
echo PASSED: Ruff check clean.
echo.

REM ------------------------------------------------
REM Step 2: Run Unit Tests
REM ------------------------------------------------
echo [2/5] Running Unit Tests...
pytest -v
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo FAILED: Unit tests failed.
    echo Fix failing tests before building.
    echo Run: pytest -v for details.
    exit /b 1
)
echo PASSED: All tests passed.
echo.

REM ------------------------------------------------
REM Step 3: Clean previous build artifacts
REM ------------------------------------------------
echo [3/5] Cleaning previous build artifacts...
if exist dist (
    rmdir /s /q dist
    echo Removed dist/ folder.
)
if exist build (
    rmdir /s /q build
    echo Removed build/ folder.
)
REM any other python cache build files/folders to delete
echo DONE: Clean complete.
echo.

REM ------------------------------------------------
REM Step 4: Build CLI Executable
REM ------------------------------------------------
echo [4/5] Building CLI executable...
pyinstaller --clean --noconfirm ^
    --name Search-documents_CLI ^
    --console ^
    --icon assets/Search-documents.ico ^
    --paths src ^
    --add-data "src\utilities;utilities" ^
    --add-data "src\writers;writers" ^
    --add-data "src\version_info.txt;." ^
    --distpath dist ^
    --workpath build ^
    src/cli/cli_main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo FAILED: CLI build failed.
    exit /b 1
)
echo PASSED: CLI build complete.
echo.

REM ------------------------------------------------
REM Step 5: Build GUI Executable
REM ------------------------------------------------
echo [5/5] Building GUI executable...
pyinstaller --clean --noconfirm ^
    --name Search-documents_GUI ^
    --windowed ^
    --icon assets/Search-documents.ico ^
    --splash assets/Search-documents.png ^
    --paths src ^
    --add-data "src\utilities;utilities" ^
    --add-data "src\writers;writers" ^
    --add-data "src\version_info.txt;." ^
    --distpath dist ^
    --workpath build ^
    src/gui/gui_main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo FAILED: GUI build failed.
    exit /b 1
)
echo PASSED: GUI build complete.
echo.

REM ------------------------------------------------
REM Build Summary
REM ------------------------------------------------
echo ================================================
echo  Build Complete!
echo ================================================
echo.
echo Executables located in dist\ folder:
echo   dist\Search-documents_CLI\Search-documents_CLI.exe
echo   dist\Search-documents_GUI\Search-documents_GUI.exe
echo.
echo ================================================