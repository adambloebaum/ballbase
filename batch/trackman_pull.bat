@echo off
setlocal

rem get today's date in YYYY-MM-DD format
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (
    set year=%%c
    set month=%%a
    set day=%%b
)

rem convert date to Julian and decrement to get yesterday
set /a jd= %year%*10000 + %month%*100 + %day% - 1

rem extract year, month, and day from Julian date
set /a year=jd/10000
set /a month=(jd%%10000)/100
set /a day=jd%%100

rem leading zero for single digit months and days
if %month% LSS 10 set month=0%month%
if %day% LSS 10 set day=0%day%

rem set and create the directory for yesterday
set DATE_DIR=C:\Users\adam.bloebaum\Documents\Trackman_Batch_Pulls\%year%-%month%-%day%
mkdir %DATE_DIR%

rem check for errors
if %errorlevel% == 0 (
    echo Error occurred during file transfer.
    rem additional error handling
) else (
    echo File transfer completed successfully.
)

rem call WinSCP script for yesterday's date
"C:\Program Files (x86)\WinSCP\WinSCP.com" /script=**PATH TO FILE**\trackman_pull.txt /parameter // %year% %month% %day%
