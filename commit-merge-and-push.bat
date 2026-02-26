@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo [1/3] 添加已解决冲突的文件...
git add index.js vercel.json

echo [2/3] 完成合并提交...
git commit -m "Merge remote main; resolve conflicts, keep Express app"

echo [3/3] 推送到 GitHub...
git push -u origin main
if errorlevel 1 goto err

echo.
echo 完成: https://github.com/yutangzhu/guoyu-finance
pause
exit /b 0

:err
echo 推送失败，请查看上方报错。
pause
exit /b 1
