@echo off
rem demo.bat - quick one-liner demos for --text mode
chcp 65001 >nul

set PYTHON=D:\Software\miniconda3\envs\ai\python.exe

rem Dem 1: 多语言 + Emoji
%PYTHON% main.py --text "Hello world! 你好世界！😀🔥" --output-dir output/demo/1 --no-plot

