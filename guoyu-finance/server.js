const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
app.use(express.json({ limit: '10mb' }));
app.use(express.static(path.join(__dirname, 'public')));

// ── 简单密码保护 ──────────────────────────────
const ACCESS_PASSWORD = process.env.ACCESS_PASSWORD || 'guoyu2024';

// ── 数据文件路径（Vercel 用 /tmp，本地用当前目录）──
const DATA_DIR = process.env.VERCEL ? '/tmp' : __dirname;
const DATA_FILE = path.join(DATA_DIR, 'db.json');

function readDB() {
  try {
    if (fs.existsSync(DATA_FILE)) {
      return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
    }
  } catch(e) {}
  return { transactions: [], inventory: [], arap: [] };
}

function writeDB(data) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(data), 'utf8');
}

// ── API 路由 ──────────────────────────────────

// 验证密码
app.post('/api/login', (req, res) => {
  const { password } = req.body;
  if (password === ACCESS_PASSWORD) {
    res.json({ ok: true });
  } else {
    res.status(401).json({ ok: false, msg: '密码错误' });
  }
});

// 获取全部数据
app.get('/api/data', (req, res) => {
  const pwd = req.headers['x-password'];
  if (pwd !== ACCESS_PASSWORD) return res.status(401).json({ msg: '未授权' });
  res.json(readDB());
});

// 保存全部数据
app.post('/api/data', (req, res) => {
  const pwd = req.headers['x-password'];
  if (pwd !== ACCESS_PASSWORD) return res.status(401).json({ msg: '未授权' });
  writeDB(req.body);
  res.json({ ok: true });
});

// 健康检查
app.get('/api/ping', (req, res) => res.json({ ok: true, time: new Date().toISOString() }));

// 所有其他路由返回 index.html
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`国宇制冷财务管家 运行在 http://localhost:${PORT}`));

module.exports = app;
