@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo [1/5] 初始化 Git...
git init
if errorlevel 1 goto err

echo [2/5] 添加远程仓库...
git remote remove origin 2>nul
git remote add origin https://github.com/yutangzhu/guoyu-finance.git
if errorlevel 1 goto err

echo [3/5] 添加所有文件并提交...
git add .
git commit -m "Initial commit: Guoyu Finance"
if errorlevel 1 (
  echo 提示: 若显示 "nothing to commit"，说明没有新文件，可忽略。
)

echo [4/5] 设置主分支为 main...
git branch -M main

echo [5/5] 推送到 GitHub...
git push -u origin main
if errorlevel 1 goto err

echo.
echo 完成。仓库: https://github.com/yutangzhu/guoyu-finance
echo Vercel 会在连接 Git 后自动部署。
pause
exit /b 0

:err
echo.
echo 执行出错。若 push 失败，请检查:
echo - 已登录 GitHub (或配置好凭据)
echo - 仓库 https://github.com/yutangzhu/guoyu-finance 已存在且有权限
pause
exit /b 1
