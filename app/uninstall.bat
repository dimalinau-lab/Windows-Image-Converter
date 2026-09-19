@echo off
chcp 65001 > nul
cd /d "%~dp0"

if exist python.exe (
    start "" python.exe main.py --uninstall
) else (
    start "" pythonw.exe main.py --uninstall
)