module.exports = (req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end('<h1>服务自检：正常</h1><p>如果你能看到这个页面，说明网络和 Vercel 基础环境没问题。</p>');
};
