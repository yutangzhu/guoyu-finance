const express = require("express");
const app = express();

// 1. 必须配置：允许解析 JSON（如果你有 POST 请求）
app.use(express.json());

// 2. 修复后的首页路由：去掉原先代码里的重复嵌套循环
app.get("/", (req, res) => {
  res.send(`
    <h1>Guoyu Finance 部署成功</h1>
    <p>状态：运行正常 (Ready)</p>
    <p>最后更新时间：${new Date().toLocaleString()}</p>
  `);
});

// 3. 错误处理：防止程序崩溃
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('服务器内部错误');
});

// 4. 重要：Vercel 环境不需要 app.listen，但为了本地测试可以保留
const PORT = process.env.PORT || 3000;
if (process.env.NODE_ENV !== 'production') {
  app.listen(PORT, () => {
    console.log(`本地测试地址: http://localhost:${PORT}`);
  });
}

// 5. 核心：必须导出 app 供 Vercel 的 Serverless Functions 调用
module.exports = app;
