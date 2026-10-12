@echo off
chcp 65001 > nul
title RozeText Mobile Tunnel
cd /d "%~dp0"
echo ============================================================
echo   RozeText Studio - Mobile Access Tunnel
echo ============================================================
python scripts\mobile_tunnel.py
pause
