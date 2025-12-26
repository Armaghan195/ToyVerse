@echo off
title ToyVerse Launcher

echo ===================================================
echo     To The Moon! (ToyVerse Launching...) 🚀
echo ===================================================

echo.
echo [1/2] Launching Backend Server...
start "ToyVerse Backend" /D "ToyVerse-Backend" cmd /k "npm run dev"

echo [2/2] Launching Frontend Server...
start "ToyVerse Frontend" /D "ToyVerse-Frontend" cmd /k "npm run dev"

echo.
echo ===================================================
echo   Success! Check the new windows.
echo   - Backend: http://localhost:8000
echo   - Frontend: http://localhost:5173
echo ===================================================
pause
