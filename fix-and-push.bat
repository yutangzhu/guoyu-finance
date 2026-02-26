@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo 已配置 Git 用户（本仓库）：yutangzhu
echo.
echo [1/3] 添加并提交...
git add .
git commit -m "Initial commit: Guoyu Finance"
if errorlevel 1 goto err

echo [2/3] 分支 main...
git branch -M main

echo [3/3] 推送到 GitHub...
git push -u origin main
if errorlevel 1 goto err

echo.
echo 完成: https://github.com/yutangzhu/guoyu-finance
pause
exit /b 0

:err
echo 执行出错，请查看上方报错。
pause
exit /b 1
