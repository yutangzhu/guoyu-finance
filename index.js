const express = require("express");
const app = express();

// 1. 中间件配置：允许解析 JSON
app.use(express.json());

// 2. 修复后的首页路由：去掉了原代码中的死循环嵌套
app.get("/", (req, res) => {
  res.status(200).send(`
    <div style="font-family: sans-serif; text-align: center; padding-top: 50px;">
      <h1>🚀 Guoyu Finance 部署成功！</h1>
      <p>状态：后端运行正常</p>
      <p>更新时间：${new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}</p>
      <hr style="width: 200px; margin: 20px auto;">
      <p style="color: #666;">Timeout 问题已修复，现在你可以开始添加业务代码了。</p>
    </div>
  `);
});

// 3. 错误处理：捕获潜在崩溃
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('服务器内部错误');
});

// 4. 重要：Vercel 环境不需要 app.listen，但保留它以便你在本地开发测试
const PORT = process.env.PORT || 3000;
if (process.env.NODE_ENV !== 'production') {
  app.listen(PORT, () => {
    console.log(`本地测试地址: http://localhost:${PORT}`);
  });
}

// 5. 核心：必须导出 app 供 Vercel 的 Serverless 环境使用
module.exports = app;
