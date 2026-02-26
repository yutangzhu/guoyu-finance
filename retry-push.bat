@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo 增大 Git 缓冲区（可能改善大推送稳定性）...
git config http.postBuffer 524288000

echo.
echo 正在推送到 GitHub，若失败会自动重试 3 次...
echo.

set try=1
:retry
echo [尝试 %try%/3] git push -u origin main
git push -u origin main
if not errorlevel 1 goto ok
set /a try+=1
if %try% gtr 3 goto fail
echo 等待 5 秒后重试...
timeout /t 5 /nobreak >nul
goto retry

:ok
echo.
echo 推送成功: https://github.com/yutangzhu/guoyu-finance
pause
exit /b 0

:fail
echo.
echo 多次推送仍失败，多为网络或访问 GitHub 不稳定，请查看下方「排查建议」。
pause
exit /b 1
