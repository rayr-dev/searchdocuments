@echo off
setlocal enabledelayedexpansion

echo ================================================
echo  Search Documents - Post Build Smoke Tests
echo ================================================
echo.

REM ------------------------------------------------
REM Configuration
REM ------------------------------------------------
set CLI=python src\cli\cli_main.py
set TESTDATA=testdata
set REPORTS=testdata\reports\smoketest
set PASS_COUNT=0
set FAIL_COUNT=0
set FAIL_LIST=

REM ------------------------------------------------
REM Helper: Run scenario and extract summary values
REM ------------------------------------------------
REM Usage: call :run_scenario <name> <source> <target> <flags>
REM Results stored in SUMMARY_TEXT variable

REM ------------------------------------------------
REM Regenerate test data
REM ------------------------------------------------
echo [SETUP] Regenerating test data...
python tools\create_testdata.py --clean --base %TESTDATA%
if %ERRORLEVEL% NEQ 0 (
    echo FAILED: Could not generate test data.
    exit /b 1
)
echo DONE: Test data ready.
echo.

REM ------------------------------------------------
REM Clean previous smoke test reports
REM ------------------------------------------------
if exist %REPORTS% (
    rmdir /s /q %REPORTS%
)
mkdir %REPORTS%

REM ================================================
REM SCENARIO 1 - Identical Files
REM ================================================
echo [S1] Scenario 1 - Identical Files...
set S=scenario1_same
%CLI% %TESTDATA%\%S%\source %TESTDATA%\%S%\target -o %REPORTS%\%S% --findall > %REPORTS%\%S%_output.txt 2>&1
call :check_result "S1" "%REPORTS%\%S%_output.txt" "Total Files in Source:      9" "S1-SrcFiles"
call :check_result "S1" "%REPORTS%\%S%_output.txt" "Total Files in Target:      9" "S1-TgtFiles"
call :check_result "S1" "%REPORTS%\%S%_output.txt" "Unique filenames in Source: 5" "S1-SrcUniq"
call :check_result "S1" "%REPORTS%\%S%_output.txt" "Unique filenames in Target: 5" "S1-TgtUniq"
call :check_result "S1" "%REPORTS%\%S%_output.txt" "Total Exact Matches:        9" "S1-Matches"
call :check_result "S1" "%REPORTS%\%S%_output.txt" "Total Mismatches:           0" "S1-Mismatches"
call :check_result "S1" "%REPORTS%\%S%_output.txt" "Total Missing Files:        0" "S1-Missing"
call :check_result "S1" "%REPORTS%\%S%_output.txt" "Multi-Match Cases:          3" "S1-Multi"
call :check_result "S1" "%REPORTS%\%S%_output.txt" "Mixed Match/Mismatch:       0" "S1-Mixed"
echo.

REM ================================================
REM SCENARIO 2 - Mixed Results
REM ================================================
echo [S2] Scenario 2 - Mixed Results...
set S=scenario2_mixed
%CLI% %TESTDATA%\%S%\source %TESTDATA%\%S%\target -o %REPORTS%\%S% --findall > %REPORTS%\%S%_output.txt 2>&1
call :check_result "S2" "%REPORTS%\%S%_output.txt" "Total Files in Source:      18" "S2-SrcFiles"
call :check_result "S2" "%REPORTS%\%S%_output.txt" "Total Files in Target:      17" "S2-TgtFiles"
call :check_result "S2" "%REPORTS%\%S%_output.txt" "Unique filenames in Source: 8"  "S2-SrcUniq"
call :check_result "S2" "%REPORTS%\%S%_output.txt" "Unique filenames in Target: 7"  "S2-TgtUniq"
call :check_result "S2" "%REPORTS%\%S%_output.txt" "Total Exact Matches:        11" "S2-Matches"
call :check_result "S2" "%REPORTS%\%S%_output.txt" "Total Mismatches:           3"  "S2-Mismatches"
call :check_result "S2" "%REPORTS%\%S%_output.txt" "Total Missing Files:        1"  "S2-Missing"
call :check_result "S2" "%REPORTS%\%S%_output.txt" "Multi-Match Cases:          4"  "S2-Multi"
call :check_result "S2" "%REPORTS%\%S%_output.txt" "Mixed Match/Mismatch:       0"  "S2-Mixed"
echo.

REM ================================================
REM SCENARIO 3 - Empty Source
REM ================================================
echo [S3] Scenario 3 - Empty Source...
set S=scenario3_empty_source
%CLI% %TESTDATA%\%S%\source %TESTDATA%\%S%\target -o %REPORTS%\%S% --findall > %REPORTS%\%S%_output.txt 2>&1
call :check_result "S3" "%REPORTS%\%S%_output.txt" "Total Files in Source:      0" "S3-SrcFiles"
call :check_result "S3" "%REPORTS%\%S%_output.txt" "Total Files in Target:      6" "S3-TgtFiles"
call :check_result "S3" "%REPORTS%\%S%_output.txt" "Unique filenames in Source: 0" "S3-SrcUniq"
call :check_result "S3" "%REPORTS%\%S%_output.txt" "Unique filenames in Target: 4" "S3-TgtUniq"
call :check_result "S3" "%REPORTS%\%S%_output.txt" "Total Exact Matches:        0" "S3-Matches"
call :check_result "S3" "%REPORTS%\%S%_output.txt" "Total Mismatches:           0" "S3-Mismatches"
call :check_result "S3" "%REPORTS%\%S%_output.txt" "Total Missing Files:        0" "S3-Missing"
call :check_result "S3" "%REPORTS%\%S%_output.txt" "Multi-Match Cases:          0" "S3-Multi"
call :check_result "S3" "%REPORTS%\%S%_output.txt" "Mixed Match/Mismatch:       0" "S3-Mixed"
echo.

REM ================================================
REM SCENARIO 4 - Empty Target
REM ================================================
echo [S4] Scenario 4 - Empty Target...
set S=scenario4_empty_target
%CLI% %TESTDATA%\%S%\source %TESTDATA%\%S%\target -o %REPORTS%\%S% --findall > %REPORTS%\%S%_output.txt 2>&1
call :check_result "S4" "%REPORTS%\%S%_output.txt" "Total Files in Source:      6" "S4-SrcFiles"
call :check_result "S4" "%REPORTS%\%S%_output.txt" "Total Files in Target:      0" "S4-TgtFiles"
call :check_result "S4" "%REPORTS%\%S%_output.txt" "Unique filenames in Source: 4" "S4-SrcUniq"
call :check_result "S4" "%REPORTS%\%S%_output.txt" "Unique filenames in Target: 0" "S4-TgtUniq"
call :check_result "S4" "%REPORTS%\%S%_output.txt" "Total Exact Matches:        0" "S4-Matches"
call :check_result "S4" "%REPORTS%\%S%_output.txt" "Total Mismatches:           0" "S4-Mismatches"
call :check_result "S4" "%REPORTS%\%S%_output.txt" "Total Missing Files:        4" "S4-Missing"
call :check_result "S4" "%REPORTS%\%S%_output.txt" "Multi-Match Cases:          0" "S4-Multi"
call :check_result "S4" "%REPORTS%\%S%_output.txt" "Mixed Match/Mismatch:       0" "S4-Mixed"
echo.

REM ================================================
REM SCENARIO 5 - Deep Nested
REM ================================================
echo [S5] Scenario 5 - Deep Nested...
set S=scenario5_deep_nested
%CLI% %TESTDATA%\%S%\source %TESTDATA%\%S%\target -o %REPORTS%\%S% --findall > %REPORTS%\%S%_output.txt 2>&1
call :check_result "S5" "%REPORTS%\%S%_output.txt" "Total Files in Source:      5" "S5-SrcFiles"
call :check_result "S5" "%REPORTS%\%S%_output.txt" "Total Files in Target:      5" "S5-TgtFiles"
call :check_result "S5" "%REPORTS%\%S%_output.txt" "Unique filenames in Source: 5" "S5-SrcUniq"
call :check_result "S5" "%REPORTS%\%S%_output.txt" "Unique filenames in Target: 5" "S5-TgtUniq"
call :check_result "S5" "%REPORTS%\%S%_output.txt" "Total Exact Matches:        5" "S5-Matches"
call :check_result "S5" "%REPORTS%\%S%_output.txt" "Total Mismatches:           0" "S5-Mismatches"
call :check_result "S5" "%REPORTS%\%S%_output.txt" "Total Missing Files:        0" "S5-Missing"
call :check_result "S5" "%REPORTS%\%S%_output.txt" "Multi-Match Cases:          0" "S5-Multi"
call :check_result "S5" "%REPORTS%\%S%_output.txt" "Mixed Match/Mismatch:       0" "S5-Mixed"
echo.

REM ================================================
REM SCENARIO 6 - Special Characters
REM ================================================
echo [S6] Scenario 6 - Special Characters...
set S=scenario6_special_chars
%CLI% %TESTDATA%\%S%\source %TESTDATA%\%S%\target -o %REPORTS%\%S% --findall > %REPORTS%\%S%_output.txt 2>&1
call :check_result "S6" "%REPORTS%\%S%_output.txt" "Total Files in Source:      9" "S6-SrcFiles"
call :check_result "S6" "%REPORTS%\%S%_output.txt" "Total Files in Target:      9" "S6-TgtFiles"
call :check_result "S6" "%REPORTS%\%S%_output.txt" "Unique filenames in Source: 9" "S6-SrcUniq"
call :check_result "S6" "%REPORTS%\%S%_output.txt" "Unique filenames in Target: 9" "S6-TgtUniq"
call :check_result "S6" "%REPORTS%\%S%_output.txt" "Total Exact Matches:        9" "S6-Matches"
call :check_result "S6" "%REPORTS%\%S%_output.txt" "Total Mismatches:           0" "S6-Mismatches"
call :check_result "S6" "%REPORTS%\%S%_output.txt" "Total Missing Files:        0" "S6-Missing"
call :check_result "S6" "%REPORTS%\%S%_output.txt" "Multi-Match Cases:          0" "S6-Multi"
call :check_result "S6" "%REPORTS%\%S%_output.txt" "Mixed Match/Mismatch:       0" "S6-Mixed"
echo.

REM ================================================
REM SCENARIO 7a - Corrupted Files (Fast Mode)
REM ================================================
echo [S7a] Scenario 7 - Corrupted Files (Fast Mode)...
set S=scenario7_corrupted
%CLI% %TESTDATA%\%S%\source %TESTDATA%\%S%\target -o %REPORTS%\%S%_fast --findall > %REPORTS%\%S%_fast_output.txt 2>&1
call :check_result "S7a" "%REPORTS%\%S%_fast_output.txt" "Total Files in Source:      3" "S7a-SrcFiles"
call :check_result "S7a" "%REPORTS%\%S%_fast_output.txt" "Total Files in Target:      3" "S7a-TgtFiles"
call :check_result "S7a" "%REPORTS%\%S%_fast_output.txt" "Unique filenames in Source: 3" "S7a-SrcUniq"
call :check_result "S7a" "%REPORTS%\%S%_fast_output.txt" "Unique filenames in Target: 3" "S7a-TgtUniq"
call :check_result "S7a" "%REPORTS%\%S%_fast_output.txt" "Total Exact Matches:        3" "S7a-Matches"
call :check_result "S7a" "%REPORTS%\%S%_fast_output.txt" "Total Mismatches:           0" "S7a-Mismatches"
call :check_result "S7a" "%REPORTS%\%S%_fast_output.txt" "Total Missing Files:        0" "S7a-Missing"
call :check_result "S7a" "%REPORTS%\%S%_fast_output.txt" "Multi-Match Cases:          0" "S7a-Multi"
call :check_result "S7a" "%REPORTS%\%S%_fast_output.txt" "Mixed Match/Mismatch:       0" "S7a-Mixed"
echo.

REM ================================================
REM SCENARIO 7b - Corrupted Files (Hash Only Mode)
REM ================================================
echo [S7b] Scenario 7 - Corrupted Files (Hash Only Mode)...
set S=scenario7_corrupted
%CLI% %TESTDATA%\%S%\source %TESTDATA%\%S%\target -o %REPORTS%\%S%_hash --findall --hashonly > %REPORTS%\%S%_hash_output.txt 2>&1
call :check_result "S7b" "%REPORTS%\%S%_hash_output.txt" "Total Files in Source:      3" "S7b-SrcFiles"
call :check_result "S7b" "%REPORTS%\%S%_hash_output.txt" "Total Files in Target:      3" "S7b-TgtFiles"
call :check_result "S7b" "%REPORTS%\%S%_hash_output.txt" "Unique filenames in Source: 3" "S7b-SrcUniq"
call :check_result "S7b" "%REPORTS%\%S%_hash_output.txt" "Unique filenames in Target: 3" "S7b-TgtUniq"
call :check_result "S7b" "%REPORTS%\%S%_hash_output.txt" "Total Exact Matches:        0" "S7b-Matches"
call :check_result "S7b" "%REPORTS%\%S%_hash_output.txt" "Total Mismatches:           3" "S7b-Mismatches"
call :check_result "S7b" "%REPORTS%\%S%_hash_output.txt" "Total Missing Files:        0" "S7b-Missing"
call :check_result "S7b" "%REPORTS%\%S%_hash_output.txt" "Multi-Match Cases:          0" "S7b-Multi"
call :check_result "S7b" "%REPORTS%\%S%_hash_output.txt" "Mixed Match/Mismatch:       0" "S7b-Mixed"
echo.
REM ================================================
REM RESULTS SUMMARY
REM ================================================
echo ================================================
echo  Smoke Test Results
echo ================================================
echo.
echo   PASSED: %PASS_COUNT%
echo   FAILED: %FAIL_COUNT%
echo.

if %FAIL_COUNT% GTR 0 (
    echo Failed checks:
    for %%F in (%FAIL_LIST%) do echo   - %%F
    echo.
    echo SMOKE TESTS FAILED
    exit /b 1
) else (
    echo All smoke tests PASSED!
    exit /b 0
)

REM ================================================
REM Subroutine: check_result
REM Usage: call :check_result <scenario> <file> <expected_string> <check_name>
REM ================================================
:check_result
set _SCENARIO=%~1
set _FILE=%~2
set _EXPECTED=%~3
set _NAME=%~4

findstr /c:"%_EXPECTED%" "%_FILE%" > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   PASS [%_NAME%]: %_EXPECTED%
    set /a PASS_COUNT+=1
) else (
    echo   FAIL [%_NAME%]: Expected: "%_EXPECTED%"
    set /a FAIL_COUNT+=1
    set FAIL_LIST=%FAIL_LIST% %_NAME%
)
goto :eof