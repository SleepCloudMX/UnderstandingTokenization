@echo off
:: lang.bat — 逐一运行 lang/ 下的每个子任务
:: 每个子任务输出到对应的镜像目录，如 output/lang/en_main/
::
:: 用法：
::   scripts\lang.bat
::   scripts\lang.bat gpt-4o          （指定 tiktoken 模型）

setlocal EnableDelayedExpansion

:: ---- 配置 ----
set PYTHON=D:\Software\miniconda3\envs\ai\python.exe
set MODEL=%~1
if "%MODEL%"=="" set MODEL=gpt-4o

:: ---- 子任务列表 ----
set SUBPATHS=lang/en_main lang/zh_main

echo ============================================================
echo  lang.bat  ^|  tokenizer=tiktoken  model=%MODEL%
echo ============================================================

for %%S in (%SUBPATHS%) do (
    echo.
    echo [TASK] %%S
    echo ------------------------------------------------------------
    %PYTHON% main.py ^
        --subpath %%S ^
        --tokenizer tiktoken ^
        --model %MODEL% ^
        --output-prefix results ^
        --warn-errors
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
