@echo off
rem run_all.bat - run ALL subgroups under data/ one by one
rem Output mirrors to output/<subpath>/
rem
rem Usage:
rem   scripts\run_all.bat
rem   scripts\run_all.bat gpt-4o-mini   (optional: specify tiktoken model)

chcp 65001 >nul
setlocal EnableDelayedExpansion

rem ---- config ----
set PYTHON=D:\Software\miniconda3\envs\ai\python.exe
set MODEL=%~1
if "%MODEL%"=="" set MODEL=gpt-4o

rem ---- subpath list ----
rem Single-level: code  emoji  extreme  format  num_symbol
rem Two-level:    lang/en_main  lang/zh_main  lang/zhc_main
set SUBPATHS=code emoji extreme format num_symbol lang/en_main lang/zh_main lang/zhc_main

echo ============================================================
echo  run_all.bat  ^|  tokenizer=tiktoken  model=%MODEL%
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
echo  All tasks completed.
echo ============================================================
endlocal
