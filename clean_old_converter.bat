@echo off
chcp 65001 > nul
:: Запрос прав администратора при необходимости
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Запрос прав администратора для очистки реестра...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~f0\"' -Verb RunAs"
    exit /b
)

echo Очистка старых записей Converter из реестра Windows...

:: Удаление старых веток HKLM
reg delete "HKLM\SOFTWARE\Classes\SystemFileAssociations\.docx\shell\ConvertToPdf" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Classes\SystemFileAssociations\.docx\shell\MyDocConverter" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Classes\SystemFileAssociations\.doc\shell\ConvertToPdf" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Classes\SystemFileAssociations\.doc\shell\MyDocConverter" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Classes\SystemFileAssociations\.pdf\shell\ConvertToDocx" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Classes\SystemFileAssociations\.pdf\shell\MyPdfConverter" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Classes\SystemFileAssociations\image\shell\MyPyConverter" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Classes\MyDocConverter" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Classes\MyPdfConverter" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Classes\MyPyConverter" /f >nul 2>&1

:: Удаление старых веток HKCU
reg delete "HKCU\Software\Classes\SystemFileAssociations\.docx\shell\ConvertToPdf" /f >nul 2>&1
reg delete "HKCU\Software\Classes\SystemFileAssociations\.docx\shell\MyDocConverter" /f >nul 2>&1
reg delete "HKCU\Software\Classes\SystemFileAssociations\.doc\shell\ConvertToPdf" /f >nul 2>&1
reg delete "HKCU\Software\Classes\SystemFileAssociations\.doc\shell\MyDocConverter" /f >nul 2>&1
reg delete "HKCU\Software\Classes\SystemFileAssociations\.pdf\shell\ConvertToDocx" /f >nul 2>&1
reg delete "HKCU\Software\Classes\SystemFileAssociations\.pdf\shell\MyPdfConverter" /f >nul 2>&1
reg delete "HKCU\Software\Classes\SystemFileAssociations\image\shell\MyPyConverter" /f >nul 2>&1
reg delete "HKCU\Software\Classes\MyDocConverter" /f >nul 2>&1
reg delete "HKCU\Software\Classes\MyPdfConverter" /f >nul 2>&1
reg delete "HKCU\Software\Classes\MyPyConverter" /f >nul 2>&1

echo Старые пункты успешно удалены!
timeout /t 3 >nul
