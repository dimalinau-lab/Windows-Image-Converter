@echo off
chcp 65001 >nul
title Converter Uninstaller
cd /d "%~dp0"

if exist "Converter.exe" (
    start "" "Converter.exe" --uninstall
) else (
    python app\uninstaller.py
)
