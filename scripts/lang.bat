@echo off
rem lang.bat - run each subgroup under lang/ one by one
rem Output mirrors to output/lang/<subgroup>/
rem
rem Usage:
rem   scripts\lang.bat
rem   scripts\lang.bat gpt-4o-mini   (optional: specify tiktoken model)

chcp 65001 >nul
setlocal EnableDelayedExpansion

rem ---- config ----
set PYTHON=D:\Software\miniconda3\envs\ai\python.exe
set MODEL=%~1
if "%MODEL%"=="" set MODEL=gpt-4o

rem ---- subpath list ----
set SUBPATHS=lang/en_main lang/zh_main

echo ============================================================
echo  lang.bat  ^|  tokenizer=tiktoken  model=%MODEL%
echo ============================================================

for %%S in (%SUBPATHS%) do (
    echo.
    echo [TASK] %%S
    echo ------------------------------------------------------------
    %PYTHON% main.py --subpath %%S --tokenizer tiktoken --model %MODEL% --output-prefix results --warn-errors
    if errorlevel 1 (
        echo [ERROR] %%S failed.
        exit /b 1
    )
)

echo.
echo ============================================================
echo  All lang tasks completed.
echo ============================================================
endlocal
