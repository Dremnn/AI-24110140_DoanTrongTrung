@echo off
chcp 65001 > nul
echo ===================================================
echo     AI Search Lab - 8-Puzzle ^& Vacuum World
echo     BFS * DFS * UCS (Dark Mode UI)
echo ===================================================

set "PY312=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe"

if exist "%PY312%" (
    echo Dang khoi chay bang Python 3.12: %PY312%
    "%PY312%" "%~dp0main.py"
) else (
    echo Dang khoi chay bang python he thong...
    python "%~dp0main.py"
)

if errorlevel 1 (
    echo.
    echo [LOI] Chuong trinh ket thuc voi loi. Nhan phim bat ky de thoat...
    pause > nul
)
