@echo off
set PROJECT_PATH=.

REM Activate the virtual environment

call "%PROJECT_PATH%\env\Scripts\activate.bat"

REM launch streamlit main

streamlit run "%PROJECT_PATH%\main.py"