@echo off
REM Run the Python script and keep the terminal open
python update_versions.py

REM Prevent the terminal from closing immediately
echo.
echo Script execution completed. Press any key to exit.
pause
