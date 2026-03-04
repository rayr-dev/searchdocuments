@echo off
REM post_build_test.cmd
REM Runs after successful build to validate executable behavior

echo ================================================
echo  Post-Build Integration Tests
echo ================================================
echo.

SET CLI=dist\Search-documents_CLI.exe
SET TESTDATA=testdata
SET REPORTS=%TESTDATA%\reports
SET PASS=0
SET FAIL=0

REM ------------------------------------------------
REM Test 1 - Same Data (all matches)
REM ------------------------------------------------
echo [TEST 1] Same Data - All Exact Matches...
%CLI% %TESTDATA%\scenario1_same\source %TESTDATA%\scenario1_same\target -o %REPORTS%\scenario1
if %ERRORLEVEL% NEQ 0 (
    echo FAILED: Test 1 - CLI returned error
    set /a FAIL+=1
) else (
    REM Validate summary output contains expected results
    findstr /c:"Total Exact Matches:" %REPORTS%\scenario1\summary.txt
    if %ERRORLEVEL% NEQ 0 (
        echo FAILED: Test 1 - Summary not generated
        set /a FAIL+=1
    ) else (
        echo PASSED: Test 1
        set /a PASS+=1
    )
)
echo.

REM ------------------------------------------------
REM Test 2 - Mixed with Find All Files
REM ------------------------------------------------
echo [TEST 2] Mixed - Find All Files enabled...
%CLI% %TESTDATA%\scenario2_mixed\source %TESTDATA%\scenario2_mixed\target -o %REPORTS%\scenario2 --findall
if %ERRORLEVEL% NEQ 0 (
    echo FAILED: Test 2 - CLI returned error
    set /a FAIL+=1
) else (
    echo PASSED: Test 2
    set /a PASS+=1
)
echo.

REM ------------------------------------------------
REM Test 3 - Empty Source
REM ------------------------------------------------
echo [TEST 3] No Data - Empty Source...
%CLI% %TESTDATA%\scenario3_empty_source\source %TESTDATA%\scenario3_empty_source\target -o %REPORTS%\scenario3
if %ERRORLEVEL% NEQ 0 (
    echo FAILED: Test 3 - CLI returned error
    set /a FAIL+=1
) else (
    echo PASSED: Test 3
    set /a PASS+=1
)
echo.

REM ------------------------------------------------
REM Test 4 - Empty Target
REM ------------------------------------------------
echo [TEST 4] No Data - Empty Target...
%CLI% %TESTDATA%\scenario4_empty_target\source %TESTDATA%\scenario4_empty_target\target -o %REPORTS%\scenario4
if %ERRORLEVEL% NEQ 0 (
    echo FAILED: Test 4 - CLI returned error
    set /a FAIL+=1
) else (
    echo PASSED: Test 4
    set /a PASS+=1
)
echo.

REM ------------------------------------------------
REM Test 5 - Mixed Find All Files disabled
REM ------------------------------------------------
echo [TEST 5] Mixed - Find All Files disabled...
%CLI% %TESTDATA%\scenario5_mixed_no_findall\source %TESTDATA%\scenario5_mixed_no_findall\target -o %REPORTS%\scenario5
if %ERRORLEVEL% NEQ 0 (
    echo FAILED: Test 5 - CLI returned error
    set /a FAIL+=1
) else (
    echo PASSED: Test 5
    set /a PASS+=1
)
echo.

REM ------------------------------------------------
REM Test Summary
REM ------------------------------------------------
echo ================================================
echo  Integration Test Results
echo ================================================
echo  Passed: %PASS%
echo  Failed: %FAIL%
echo ================================================

if %FAIL% GTR 0 (
    echo WARNING: Some integration tests failed!
    echo Review reports in %REPORTS%
    exit /b 1
)

echo All integration tests passed!
exit /b 0