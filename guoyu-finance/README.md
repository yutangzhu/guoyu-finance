# 国宇制冷财务管家

## 部署步骤（按顺序操作）

### 第一步：上传代码到 GitHub
1. 打开 github.com，登录你的账号
2. 点击右上角 "+" → "New repository"
3. Repository name 填：`guoyu-finance`
4. 选择 Private（私有，更安全）
5. 点击 "Create repository"
6. 点击 "uploading an existing file"
7. 把这个文件夹里的所有文件拖进去
8. 点击 "Commit changes"

### 第二步：部署到 Vercel
1. 打开 vercel.com，点击 "Sign Up"
2. 选择 "Continue with GitHub"，授权登录
3. 点击 "Add New Project"
4. 找到 guoyu-finance，点击 "Import"
5. 展开 "Environment Variables"，添加：
   - Name: `ACCESS_PASSWORD`
   - Value: 你想设置的访问密码（比如 guoyu2024）
6. 点击 "Deploy"
7. 等待约1分钟，部署完成后会给你一个网址

### 第三步：访问使用
- 电脑/手机浏览器打开 Vercel 给的网址
- 输入你设置的访问密码
- 开始使用！

## 修改访问密码
在 Vercel 控制台 → Settings → Environment Variables 中修改 ACCESS_PASSWORD
