@echo off
setlocal

rem set path to the Python executable in the Conda environment
set PYTHON_EXE=**PATH TO PYTHON EXECUTABLE ENVIRONMENT**

rem run the Python script using the Python executable in the Conda environment
"%PYTHON_EXE%" **PATH TO FILE**\trackman_viz.py
