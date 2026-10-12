@echo off
chcp 65001 > nul
title RozeText - Sync to Cloud
cd /d "%~dp0"
echo ============================================================
echo   RozeText Studio - همگام‌سازی دیتابیس با گیت‌هاب و رندر
echo ============================================================
echo در حال ذخیره و ارسال دیتابیس به گیت‌هاب و سرور ابری...
git add data/ published-content-history.md
git commit -m "chore: sync latest hunted scripts and database"
git push origin main
echo.
echo ============================================================
echo ✅ همگام‌سازی با موفقیت انجام شد!
echo دیتای جدید به گیت‌هاب ارسال شد و سرور Render خودکار آپدیت می‌شود.
echo ============================================================
pause
