@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo [1/2] 拉取远程并合并（保留两边提交）...
git pull origin main --allow-unrelated-histories --no-edit
if errorlevel 1 (
  echo 若有冲突，请根据提示解决后执行: git add . ^&^& git commit -m "Merge remote" ^&^& git push -u origin main
  pause
  exit /b 1
)

echo [2/2] 推送到 GitHub...
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
