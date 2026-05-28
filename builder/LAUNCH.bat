@echo off
title GKern v2.0 — Double Launch
echo ============================================================
echo   GKern v2.0 PORTABLE PACK
echo   Launching 2 tabs in default browser...
echo ============================================================
echo.
echo   TAB 1: GENESIS — Fractal Geometry Flow Explorer
echo   TAB 2: navierHunt — NS Benchmark Dashboard
echo.
echo ============================================================
start "" "%~dp0GENESIS.html"
timeout /t 1 /nobreak >nul
start "" "%~dp0navierHunt.html"
echo   Both tabs launched. You can close this window.
timeout /t 3 /nobreak >nul
