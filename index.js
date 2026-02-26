const http = require('http');
const fs = require('fs');
const path = require('path');

const PASSWORD = process.env.ACCESS_PASSWORD || 'guoyu_nanyang';
const DATA_FILE = '/tmp/guoyu_data.json';

function readDB() {
  try { if (fs.existsSync(DATA_FILE)) return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8')); } catch(e) {}
  return { transactions: [], inventory: [], arap: [] };
}
function writeDB(data) {
  try { fs.writeFileSync(DATA_FILE, JSON.stringify(data), 'utf8'); } catch(e) {}
}

const HTML = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>国宇制冷财务管家</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:"Microsoft YaHei","微软雅黑",SimHei,sans-serif;background:#f0f4fa}
::-webkit-scrollbar{width:5px}::-webkit-scrollbar-thumb{background:#cbd5e1;border-radius:10px}
#login-page{display:flex;align-items:center;justify-content:center;height:100vh;background:linear-gradient(135deg,#0f1f3d,#1a2f52)}
.login-box{background:#fff;border-radius:20px;padding:40px 36px;width:320px;box-shadow:0 24px 60px rgba(0,0,0,.3);text-align:center}
.login-logo{font-size:44px;margin-bottom:10px}
.login-title{font-size:20px;font-weight:700;color:#1e293b;margin-bottom:6px}
.login-sub{font-size:12px;color:#94a3b8;margin-bottom:26px}
.login-inp{width:100%;border:1px solid #e2e8f0;border-radius:10px;padding:12px 14px;font-size:15px;outline:none;font-family:inherit;text-align:center;letter-spacing:3px;margin-bottom:12px}
.login-inp:focus{border-color:#3b82f6;box-shadow:0 0 0 3px rgba(59,130,246,.15)}
.login-btn{width:100%;background:linear-gradient(135deg,#2563eb,#1d4ed8);color:#fff;border:none;border-radius:10px;padding:12px;font-size:15px;font-weight:600;cursor:pointer;font-family:inherit}
.login-err{color:#dc2626;font-size:12px;margin-top:8px;min-height:16px}
#app{display:none;height:100vh;overflow:hidden;flex-direction:column}
#app.show{display:flex}
.app-inner{display:flex;flex:1;overflow:hidden}
#topbar{background:linear-gradient(90deg,#0f1f3d,#1a2f52);color:#fff;padding:11px 16px;display:flex;align-items:center;justify-content:space-between}
#topbar h1{font-size:14px;font-weight:700}
#menu-btn{background:none;border:none;color:#fff;font-size:22px;cursor:pointer}
#sidebar{width:200px;background:linear-gradient(180deg,#0f1f3d,#1a2f52);display:flex;flex-direction:column;flex-shrink:0}
.logo{padding:20px 18px 12px;border-bottom:1px solid rgba(255,255,255,.08)}
.logo h1{font-size:13px;font-weight:700;color:#fff;line-height:1.4}
.logo p{font-size:11px;color:#64748b;margin-top:4px}
nav{padding:10px;flex:1;display:flex;flex-direction:column;gap:3px}
.nav-btn{display:flex;align-items:center;gap:8px;width:100%;padding:10px 12px;border-radius:10px;font-size:13px;font-weight:500;color:#94a3b8;border:none;background:transparent;cursor:pointer;text-align:left;font-family:inherit}
.nav-btn:hover{background:rgba(255,255,255,.08);color:#e2e8f0}
.nav-btn.active{background:linear-gradient(135deg,#2563eb,#1d4ed8);color:#fff}
#sync-bar{padding:7px 14px;font-size:11px;color:#475569;text-align:center;border-top:1px solid rgba(255,255,255,.06)}
#main{flex:1;overflow-y:auto}
.page{display:none;padding:22px 26px}
.page.active{display:block}
.page-title{font-size:20px;font-weight:700;color:#1e293b;margin-bottom:4px}
.page-sub{font-size:12px;color:#94a3b8}
.page-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;flex-wrap:wrap;gap:8px}
.card{background:#fff;border-radius:14px;box-shadow:0 1px 3px rgba(0,0,0,.06),0 4px 10px rgba(0,0,0,.04);padding:16px}
.kpi-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:14px}
.kpi{border-radius:12px;padding:13px 15px}
.kpi-icon{font-size:17px;color:rgba(255,255,255,.3);margin-bottom:4px}
.kpi-label{font-size:10px;color:rgba(255,255,255,.7);margin-bottom:2px}
.kpi-val{font-size:14px;font-weight:700;color:#fff}
.kpi-sub{font-size:10px;color:rgba(255,255,255,.5);margin-top:3px}
.btn{padding:8px 15px;border-radius:9px;font-size:13px;font-weight:600;border:none;cursor:pointer;font-family:inherit}
.btn-primary{background:linear-gradient(135deg,#2563eb,#1d4ed8);color:#fff}
.btn-sm{padding:4px 10px;font-size:12px;border-radius:7px;border:none;cursor:pointer;font-family:inherit;font-weight:600}
.btn-blue{background:#dbeafe;color:#1d4ed8}
.btn-red{background:#fee2e2;color:#b91c1c}
.btn-ghost{background:transparent;color:#94a3b8;border:1px solid #e2e8f0;font-family:inherit;cursor:pointer;padding:5px 11px;border-radius:8px;font-size:12px}
.inp{width:100%;border:1px solid #e2e8f0;border-radius:9px;padding:8px 10px;font-size:13px;outline:none;font-family:inherit;background:#fff;color:#1e293b}
.inp:focus{border-color:#93c5fd;box-shadow:0 0 0 3px rgba(147,197,253,.2)}
.form-label{font-size:11px;font-weight:600;color:#64748b;margin-bottom:4px;display:block}
.form-group{margin-bottom:11px}
.form-row-2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.toggle-2{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:11px}
.toggle-btn{padding:9px;border-radius:9px;border:2px solid #e2e8f0;background:#fff;color:#64748b;font-weight:600;font-size:13px;cursor:pointer;font-family:inherit}
.tbl-wrap{overflow-x:auto}
table{width:100%;border-collapse:collapse;min-width:480px}
th{padding:8px 11px;font-size:11px;font-weight:600;color:#64748b;text-align:left;background:#f8fafc;border-bottom:1px solid #f1f5f9;white-space:nowrap}
th.r,td.r{text-align:right}
td{padding:10px 11px;font-size:13px;color:#334155;border-bottom:1px solid #f8fafc}
tr:last-child td{border-bottom:none}
tr:hover td{background:#fafbff}
.badge{display:inline-block;padding:2px 7px;border-radius:20px;font-size:11px;font-weight:600}
.b-income{background:#dcfce7;color:#16a34a}.b-expense{background:#fee2e2;color:#dc2626}
.b-recv{background:#fff7ed;color:#ea580c}.b-pay{background:#fdf2f8;color:#db2777}
.b-done{background:#f0fdf4;color:#16a34a}.b-partial{background:#fefce8;color:#ca8a04}
.b-pending{background:#f8fafc;color:#64748b}.b-warn{background:#fee2e2;color:#dc2626;font-size:10px;padding:1px 5px;margin-left:4px}
.modal-overlay{display:none;position:fixed;inset:0;background:rgba(15,31,61,.5);z-index:200;align-items:center;justify-content:center;padding:16px}
.modal-overlay.open{display:flex}
.modal{background:#fff;border-radius:18px;width:100%;max-width:420px;max-height:92vh;overflow-y:auto;box-shadow:0 24px 60px rgba(0,0,0,.25)}
.modal-header{display:flex;align-items:center;justify-content:space-between;padding:14px 18px;border-bottom:1px solid #f1f5f9;position:sticky;top:0;background:#fff}
.modal-title{font-size:14px;font-weight:700;color:#1e293b}
.modal-close{background:#f1f5f9;border:none;border-radius:8px;width:26px;height:26px;cursor:pointer;font-size:13px;color:#64748b}
.modal-body{padding:16px 18px}
.stat-chips{display:flex;gap:7px;flex-wrap:wrap}
.stat-chip{background:#fff;border-radius:9px;padding:5px 11px;display:flex;align-items:center;gap:5px;box-shadow:0 1px 3px rgba(0,0,0,.06)}
.sc-label{font-size:11px;color:#64748b}.sc-val{font-size:13px;font-weight:700}
.filter-bar{display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap;align-items:center}
.tab-chips{display:flex;gap:5px;flex-wrap:wrap}
.tab-chip{padding:4px 11px;border-radius:8px;font-size:12px;font-weight:600;border:1px solid #e2e8f0;cursor:pointer;background:#fff;color:#64748b;font-family:inherit}
.tab-chip.active{background:#2563eb;color:#fff;border-color:#2563eb}
.chart-wrap{display:flex;align-items:flex-end;gap:4px;padding:8px 0}
.chart-group{display:flex;gap:2px;align-items:flex-end;flex:1;justify-content:center}
.chart-bar{border-radius:4px 4px 0 0;min-width:8px}
.chart-labels{display:flex;justify-content:space-around;margin-top:4px}
.chart-label{font-size:10px;color:#94a3b8;text-align:center;flex:1}
.cl-item{display:flex;align-items:center;gap:4px;font-size:11px;color:#64748b}
.cl-dot{width:9px;height:9px;border-radius:3px}
.dash-grid{display:grid;grid-template-columns:1fr;gap:12px;margin-bottom:12px}
.empty{text-align:center;padding:28px;color:#cbd5e1;font-size:13px}
.stock-card{background:#fef2f2;border-radius:10px;padding:9px 12px}
.alert-box{border-left:4px solid #ef4444;padding:12px 14px;background:#fff;border-radius:0 12px 12px 0;margin-top:12px}
.qty-ctrl{display:flex;align-items:center;justify-content:flex-end;gap:4px}
.qty-btn{width:22px;height:22px;border-radius:6px;background:#f1f5f9;border:none;cursor:pointer;font-size:13px;color:#475569}
.info-box{background:#f8fafc;border-radius:10px;padding:11px;margin-bottom:11px}
.info-row{display:flex;justify-content:space-between;margin-bottom:3px;font-size:12px}
.info-row:last-child{margin-bottom:0}
.pie-item{display:flex;align-items:center;padding:4px 0;border-bottom:1px solid #f8fafc;font-size:12px;gap:6px}
.pie-item:last-child{border-bottom:none}
.pie-dot{width:9px;height:9px;border-radius:3px;flex-shrink:0}
.pie-bar-bg{background:#f1f5f9;border-radius:4px;height:5px;flex:1;overflow:hidden}
.pie-bar-fill{height:100%;border-radius:4px}
.pie-val{width:72px;font-weight:600;color:#1e293b;text-align:right;white-space:nowrap;flex-shrink:0}
.mg-row{display:flex;align-items:center;gap:8px;margin-bottom:6px}
.mg-name{width:110px;font-size:11px;color:#475569;text-align:right;flex-shrink:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.mg-bar-bg{flex:1;background:#f1f5f9;border-radius:5px;height:17px;overflow:hidden}
.mg-bar-fill{height:100%;border-radius:5px}
.mg-val{width:62px;font-size:12px;font-weight:700;color:#1e293b}
.overdue-row td{background:#fff8f8}
.rpt-kpi{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:14px}
.sync-dot{width:7px;height:7px;border-radius:50%;display:inline-block;margin-right:4px}
@media(min-width:700px){
  #topbar{display:none}#sidebar{display:flex!important}
  .kpi-grid{grid-template-columns:repeat(6,1fr)}
  .dash-grid{grid-template-columns:1.4fr 1fr}
  .rpt-kpi{grid-template-columns:repeat(4,1fr)}
}
@media(max-width:699px){
  #sidebar{display:none;position:fixed;inset:0;z-index:150;width:210px}
  #sidebar.open{display:flex}
  .page{padding:14px}
}
</style>
</head>
<body>
<div id="login-page">
  <div class="login-box">
    <div class="login-logo">❄️</div>
    <div class="login-title">国宇制冷财务管家</div>
    <div class="login-sub">请输入访问密码</div>
    <input type="password" class="login-inp" id="pwd-inp" placeholder="请输入密码" onkeydown="if(event.key==='Enter')doLogin()">
    <button class="login-btn" onclick="doLogin()">进入系统</button>
    <div class="login-err" id="login-err"></div>
  </div>
</div>

<div id="app">
  <div id="topbar">
    <button id="menu-btn" onclick="document.getElementById('sidebar').classList.toggle('open')">☰</button>
    <h1>❄️ 国宇制冷财务管家</h1>
    <span id="top-sync" style="font-size:11px;color:#94a3b8"><span class="sync-dot" id="sdot" style="background:#f59e0b"></span><span id="stxt">连接中</span></span>
  </div>
  <div class="app-inner">
    <div id="sidebar">
      <div class="logo"><h1>❄️ 国宇制冷财务管家</h1><p>制冷配件批发管理</p></div>
      <nav>
        <button class="nav-btn active" onclick="go('dashboard',this)">⊞ 总　览</button>
        <button class="nav-btn" onclick="go('transactions',this)">≋ 收支记录</button>
        <button class="nav-btn" onclick="go('inventory',this)">◫ 库存管理</button>
        <button class="nav-btn" onclick="go('arap',this)">⇄ 往来账款</button>
        <button class="nav-btn" onclick="go('reports',this)">↗ 利润报表</button>
      </nav>
      <div id="sync-bar">⏳ 连接中...</div>
      <div style="padding:7px 14px;border-top:1px solid rgba(255,255,255,.06);font-size:11px;color:#334155;text-align:center">☁️ 数据存储于云端</div>
    </div>
    <div id="main">
      <div class="page active" id="page-dashboard">
        <div class="page-header"><div><div class="page-title">经营总览</div><div class="page-sub" id="today-str"></div></div><button class="btn-ghost" onclick="syncNow()">↻ 刷新</button></div>
        <div class="kpi-grid" id="kpi-grid"></div>
        <div class="dash-grid">
          <div class="card">
            <div style="font-weight:600;color:#1e293b;font-size:13px;margin-bottom:7px">近6个月收支趋势</div>
            <div style="display:flex;gap:10px;margin-bottom:6px;flex-wrap:wrap">
              <div class="cl-item"><div class="cl-dot" style="background:#10B981"></div>收入</div>
              <div class="cl-item"><div class="cl-dot" style="background:#F87171"></div>支出</div>
              <div class="cl-item"><div class="cl-dot" style="background:#60A5FA"></div>利润</div>
            </div>
            <div class="chart-wrap" id="dash-chart" style="height:150px"></div>
            <div class="chart-labels" id="dash-labels"></div>
          </div>
          <div class="card" style="overflow-y:auto;max-height:280px">
            <div style="font-weight:600;color:#1e293b;font-size:13px;margin-bottom:8px">最近收支</div>
            <div id="recent-list"></div>
          </div>
        </div>
        <div id="low-stock-wrap"></div>
      </div>
      <div class="page" id="page-transactions">
        <div class="page-header"><div class="page-title">收支记录</div><button class="btn btn-primary" onclick="openTxnModal()">+ 新增记录</button></div>
        <div class="filter-bar">
          <select class="inp" style="width:106px" id="ft-type" onchange="renderTxn()"><option value="all">全部类型</option><option value="income">收　入</option><option value="expense">支　出</option></select>
          <input type="month" class="inp" style="width:140px" id="ft-month" onchange="renderTxn()">
          <button class="btn-ghost" onclick="document.getElementById('ft-type').value='all';document.getElementById('ft-month').value='';renderTxn()">清除</button>
          <div style="margin-left:auto" class="stat-chips" id="txn-stats"></div>
        </div>
        <div class="card" style="padding:0;overflow:hidden"><div class="tbl-wrap"><table><thead><tr><th>日期</th><th>类型</th><th>分类</th><th>备注</th><th>支付</th><th class="r">金额</th><th></th></tr></thead><tbody id="txn-body"></tbody></table></div></div>
      </div>
      <div class="page" id="page-inventory">
        <div class="page-header"><div class="page-title">库存管理</div><button class="btn btn-primary" onclick="openInvModal()">+ 新增商品</button></div>
        <div class="filter-bar">
          <input type="text" class="inp" style="width:230px" placeholder="搜索商品名称/规格/供应商" id="inv-search" oninput="renderInv()">
          <div style="margin-left:auto" class="stat-chips" id="inv-stats"></div>
        </div>
        <div class="card" style="padding:0;overflow:hidden"><div class="tbl-wrap"><table><thead><tr><th>商品名称</th><th>规格</th><th>供应商</th><th class="r">进价</th><th class="r">售价</th><th class="r">毛利率</th><th class="r">库存</th><th class="r">库存价值</th><th></th></tr></thead><tbody id="inv-body"></tbody></table></div></div>
      </div>
      <div class="page" id="page-arap">
        <div class="page-header"><div class="page-title">往来账款</div><button class="btn btn-primary" onclick="openArapModal()">+ 新增账款</button></div>
        <div class="filter-bar"><div class="tab-chips" id="arap-tabs"></div><div style="margin-left:auto" class="stat-chips" id="arap-stats"></div></div>
        <div class="card" style="padding:0;overflow:hidden"><div class="tbl-wrap"><table><thead><tr><th>客户/供应商</th><th>类型</th><th>说明</th><th>日期</th><th>到期</th><th class="r">总金额</th><th class="r">待结清</th><th>状态</th><th></th></tr></thead><tbody id="arap-body"></tbody></table></div></div>
      </div>
      <div class="page" id="page-reports">
        <div class="page-header"><div class="page-title">利润报表</div><div style="display:flex;align-items:center;gap:7px"><span style="font-size:12px;color:#64748b">月份</span><input type="month" class="inp" style="width:142px" id="rpt-month" onchange="renderReports()"></div></div>
        <div class="rpt-kpi" id="rpt-kpi"></div>
        <div class="card" style="margin-bottom:12px">
          <div style="font-weight:600;color:#1e293b;font-size:13px;margin-bottom:7px">12个月收支利润趋势</div>
          <div style="display:flex;gap:10px;margin-bottom:6px;flex-wrap:wrap">
            <div class="cl-item"><div class="cl-dot" style="background:#10B981"></div>收入</div>
            <div class="cl-item"><div class="cl-dot" style="background:#F87171"></div>支出</div>
            <div class="cl-item"><div class="cl-dot" style="background:#60A5FA"></div>利润</div>
          </div>
          <div class="chart-wrap" id="rpt-chart" style="height:190px"></div>
          <div class="chart-labels" id="rpt-labels"></div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px">
          <div class="card"><div style="font-weight:600;color:#1e293b;font-size:13px;margin-bottom:8px">本月收入构成</div><div id="inc-pie"></div></div>
          <div class="card"><div style="font-weight:600;color:#1e293b;font-size:13px;margin-bottom:8px">本月支出构成</div><div id="exp-pie"></div></div>
        </div>
        <div class="card" id="mg-card" style="display:none"><div style="font-weight:600;color:#1e293b;font-size:13px;margin-bottom:10px">商品单件毛利排行</div><div id="mg-chart"></div></div>
      </div>
    </div>
  </div>
</div>

<!-- Modals -->
<div class="modal-overlay" id="m-txn"><div class="modal">
  <div class="modal-header"><span class="modal-title">新增收支记录</span><button class="modal-close" onclick="closeM('m-txn')">✕</button></div>
  <div class="modal-body">
    <div class="toggle-2"><button class="toggle-btn" id="tb-inc" onclick="setTT('income')">收　入</button><button class="toggle-btn" id="tb-exp" onclick="setTT('expense')">支　出</button></div>
    <div class="form-group"><label class="form-label">金额（元）*</label><input type="number" class="inp" id="f-amt" placeholder="请输入金额"></div>
    <div class="form-group"><label class="form-label">分类</label><select class="inp" id="f-cat"></select></div>
    <div class="form-group"><label class="form-label">日期</label><input type="date" class="inp" id="f-date"></div>
    <div class="form-group"><label class="form-label">支付方式</label><select class="inp" id="f-method"><option>现金</option><option>微信</option><option>支付宝</option><option>银行转账</option><option>对公转账</option><option>承兑汇票</option></select></div>
    <div class="form-group"><label class="form-label">备注</label><input type="text" class="inp" id="f-desc" placeholder="可选"></div>
    <button class="btn btn-primary" style="width:100%;padding:11px;font-size:14px" onclick="saveTxn()">确认添加</button>
  </div>
</div></div>

<div class="modal-overlay" id="m-inv"><div class="modal">
  <div class="modal-header"><span class="modal-title" id="inv-title">新增商品</span><button class="modal-close" onclick="closeM('m-inv')">✕</button></div>
  <div class="modal-body">
    <div class="form-group"><label class="form-label">商品名称 *</label><input type="text" class="inp" id="i-name" placeholder="例：R22压缩机"></div>
    <div class="form-group"><label class="form-label">规格型号</label><input type="text" class="inp" id="i-spec" placeholder="例：1.5P 220V"></div>
    <div class="form-group"><label class="form-label">供应商</label><input type="text" class="inp" id="i-sup"></div>
    <div class="form-row-2">
      <div class="form-group"><label class="form-label">进价（元）*</label><input type="number" class="inp" id="i-buy"></div>
      <div class="form-group"><label class="form-label">售价（元）</label><input type="number" class="inp" id="i-sell"></div>
    </div>
    <div class="form-row-2">
      <div class="form-group"><label class="form-label">库存数量</label><input type="number" class="inp" id="i-qty"></div>
      <div class="form-group"><label class="form-label">单位</label><select class="inp" id="i-unit"><option>件</option><option>台</option><option>套</option><option>个</option><option>米</option><option>公斤</option><option>桶</option><option>箱</option></select></div>
    </div>
    <input type="hidden" id="i-eid">
    <button class="btn btn-primary" style="width:100%;padding:11px;font-size:14px" id="inv-btn" onclick="saveInv()">确认添加</button>
  </div>
</div></div>

<div class="modal-overlay" id="m-arap"><div class="modal">
  <div class="modal-header"><span class="modal-title">新增往来账款</span><button class="modal-close" onclick="closeM('m-arap')">✕</button></div>
  <div class="modal-body">
    <div class="toggle-2"><button class="toggle-btn" id="tb-recv" onclick="setAT('receivable')">应　收　款</button><button class="toggle-btn" id="tb-apy" onclick="setAT('payable')">应　付　款</button></div>
    <div class="form-group"><label class="form-label" id="ar-cl">客户名称 *</label><input type="text" class="inp" id="ar-contact"></div>
    <div class="form-group"><label class="form-label">金额（元）*</label><input type="number" class="inp" id="ar-amt"></div>
    <div class="form-row-2">
      <div class="form-group"><label class="form-label">账款日期</label><input type="date" class="inp" id="ar-date"></div>
      <div class="form-group"><label class="form-label">到期日期</label><input type="date" class="inp" id="ar-due"></div>
    </div>
    <div class="form-group"><label class="form-label">备注</label><input type="text" class="inp" id="ar-desc"></div>
    <button class="btn btn-primary" style="width:100%;padding:11px;font-size:14px" onclick="saveArap()">确认添加</button>
  </div>
</div></div>

<div class="modal-overlay" id="m-pay"><div class="modal">
  <div class="modal-header"><span class="modal-title" id="pay-title">收款登记</span><button class="modal-close" onclick="closeM('m-pay')">✕</button></div>
  <div class="modal-body">
    <div class="info-box" id="pay-info"></div>
    <div class="form-group"><label class="form-label" id="pay-lbl">本次收款金额</label><input type="number" class="inp" id="pay-amt"></div>
    <button class="btn-sm btn-blue" style="margin-bottom:11px" onclick="setFullPay()">全额结清</button>
    <button class="btn btn-primary" style="width:100%;padding:11px;font-size:14px" onclick="confirmPay()">确认操作</button>
  </div>
</div></div>

<script>
var INC_CATS=["批发销售","零售销售","维修服务","其他收入"];
var EXP_CATS=["进货成本","运费","仓储费","人工费","房租","水电费","税费","维修费","其他支出"];
var PAL=["#3B82F6","#10B981","#F59E0B","#EF4444","#8B5CF6","#EC4899","#14B8A6","#F97316","#6366F1"];
var AT=[["all","全部"],["receivable","应收款"],["payable","应付款"],["pending","未结清"],["overdue","已逾期"]];
var DB={transactions:[],inventory:[],arap:[]};
var _pwd='',_timer=null,_page='dashboard';

function ss(msg,color){
  var b=document.getElementById('sync-bar'),d=document.getElementById('sdot'),t=document.getElementById('stxt');
  if(b)b.innerHTML='<span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:'+color+';margin-right:4px"></span>'+msg;
  if(d)d.style.background=color;if(t)t.textContent=msg;
}
function doLogin(){
  var p=document.getElementById('pwd-inp').value;if(!p)return;
  fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:p})})
  .then(function(r){return r.json();}).then(function(d){
    if(d.ok){_pwd=p;document.getElementById('login-page').style.display='none';document.getElementById('app').classList.add('show');load();}
    else document.getElementById('login-err').textContent='密码错误';
  }).catch(function(){document.getElementById('login-err').textContent='连接失败，请检查网络';});
}
document.getElementById('pwd-inp').addEventListener('keydown',function(e){if(e.key==='Enter')doLogin();});

function load(){
  ss('同步中...','#f59e0b');
  fetch('/api/data',{headers:{'x-password':_pwd}}).then(function(r){return r.json();}).then(function(d){
    DB=d;ss('已同步 '+ft(new Date()),'#10B981');rp();
  }).catch(function(){ss('加载失败','#ef4444');});
}
function push(){
  fetch('/api/data',{method:'POST',headers:{'Content-Type':'application/json','x-password':_pwd},body:JSON.stringify(DB)})
  .then(function(r){return r.json();}).then(function(d){if(d.ok)ss('已同步 '+ft(new Date()),'#10B981');else ss('保存失败','#ef4444');})
  .catch(function(){ss('保存失败','#ef4444');});
}
function save(){if(_timer)clearTimeout(_timer);ss('待同步...','#f59e0b');_timer=setTimeout(push,1200);}
function syncNow(){if(_timer)clearTimeout(_timer);load();}
setInterval(function(){if(_pwd)load();},60000);

function gi(id){return document.getElementById(id);}
function genId(){return Date.now().toString(36)+Math.random().toString(36).slice(2,6);}
function today(){return new Date().toISOString().slice(0,10);}
function nowM(){return new Date().toISOString().slice(0,7);}
function fm(n){return"¥"+(+(n||0)).toLocaleString("zh-CN",{minimumFractionDigits:2,maximumFractionDigits:2});}
function esc(s){return String(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}
function ft(d){return d.getHours().toString().padStart(2,"0")+":"+d.getMinutes().toString().padStart(2,"0");}
gi("today-str").textContent=new Date().toLocaleDateString("zh-CN",{year:"numeric",month:"long",day:"numeric",weekday:"long"});
gi("ft-month").value=nowM();gi("rpt-month").value=nowM();

function rp(){if(_page==="dashboard")rDash();else if(_page==="transactions")rTxn();else if(_page==="inventory")rInv();else if(_page==="arap")rArap();else if(_page==="reports")rRpt();}
var _af="all";
(function(){var tc=gi("arap-tabs");AT.forEach(function(t){var b=document.createElement("button");b.className="tab-chip"+(t[0]==="all"?" active":"");b.textContent=t[1];b.onclick=function(){document.querySelectorAll("#arap-tabs .tab-chip").forEach(function(x){x.classList.remove("active");});b.classList.add("active");_af=t[0];rArap();};tc.appendChild(b);});})();
document.querySelectorAll(".modal-overlay").forEach(function(m){m.addEventListener("click",function(e){if(e.target===m)m.classList.remove("open");});});
function openM(id){gi(id).classList.add("open");}function closeM(id){gi(id).classList.remove("open");}

function go(page,btn){
  _page=page;
  document.querySelectorAll(".nav-btn").forEach(function(b){b.classList.remove("active");});
  document.querySelectorAll(".page").forEach(function(p){p.classList.remove("active");});
  btn.classList.add("active");gi("page-"+page).classList.add("active");
  if(window.innerWidth<700)gi("sidebar").classList.remove("open");
  rp();
}

function bc(elId,lbId,data,mH){
  var mx=0;data.forEach(function(d){mx=Math.max(mx,d.inc,d.exp,Math.abs(d.pro));});if(mx===0)mx=1;
  var bars="",lbls="";
  data.forEach(function(d){
    var hi=Math.round(d.inc/mx*mH),he=Math.round(d.exp/mx*mH),hp=Math.round(Math.abs(d.pro)/mx*mH);
    bars+='<div class="chart-group"><div class="chart-bar" style="height:'+hi+'px;background:#10B981;width:10px" title="收入:'+fm(d.inc)+'"></div><div class="chart-bar" style="height:'+he+'px;background:#F87171;width:10px" title="支出:'+fm(d.exp)+'"></div><div class="chart-bar" style="height:'+hp+'px;background:'+(d.pro>=0?"#60A5FA":"#FDA4AF")+';width:10px" title="利润:'+fm(d.pro)+'"></div></div>';
    lbls+='<div class="chart-label">'+d.mo.slice(5)+'月</div>';
  });
  gi(elId).innerHTML=bars;gi(lbId).innerHTML=lbls;
}
function gmd(n){
  var r=[];for(var i=0;i<n;i++){var d=new Date();d.setMonth(d.getMonth()-(n-1-i));var mo=d.toISOString().slice(0,7);var ts=DB.transactions.filter(function(t){return t.date.indexOf(mo)===0;});var inc=ts.filter(function(t){return t.type==="income";}).reduce(function(s,t){return s+t.amount;},0);var exp=ts.filter(function(t){return t.type==="expense";}).reduce(function(s,t){return s+t.amount;},0);r.push({mo:mo,inc:inc,exp:exp,pro:inc-exp});}return r;
}

function rDash(){
  var m=nowM(),mT=DB.transactions.filter(function(t){return t.date.indexOf(m)===0;});
  var inc=mT.filter(function(t){return t.type==="income";}).reduce(function(s,t){return s+t.amount;},0);
  var exp=mT.filter(function(t){return t.type==="expense";}).reduce(function(s,t){return s+t.amount;},0);
  var pro=inc-exp,invV=DB.inventory.reduce(function(s,i){return s+i.purchase_price*i.quantity;},0);
  var tAR=DB.arap.filter(function(a){return a.type==="receivable"&&a.status!=="done";}).reduce(function(s,a){return s+(a.amount-(a.paid||0));},0);
  var tAP=DB.arap.filter(function(a){return a.type==="payable"&&a.status!=="done";}).reduce(function(s,a){return s+(a.amount-(a.paid||0));},0);
  var odN=DB.arap.filter(function(a){return a.type==="receivable"&&a.status!=="done"&&a.due_date&&a.due_date<today();}).length;
  gi("kpi-grid").innerHTML=[{l:"本月收入",v:fm(inc),s:"销售收入",bg:"linear-gradient(135deg,#16a34a,#15803d)",i:"↑"},{l:"本月支出",v:fm(exp),s:"各项支出",bg:"linear-gradient(135deg,#dc2626,#b91c1c)",i:"↓"},{l:"净利润",v:fm(pro),s:pro>=0?"盈利中":"亏损",bg:pro>=0?"linear-gradient(135deg,#2563eb,#1d4ed8)":"linear-gradient(135deg,#dc2626,#b91c1c)",i:"≈"},{l:"库存总值",v:fm(invV),s:DB.inventory.length+"种商品",bg:"linear-gradient(135deg,#7c3aed,#6d28d9)",i:"◫"},{l:"待收款",v:fm(tAR),s:odN>0?"⚠"+odN+"笔逾期":"应收账款",bg:"linear-gradient(135deg,#ea580c,#c2410c)",i:"⏳"},{l:"待付款",v:fm(tAP),s:"应付账款",bg:"linear-gradient(135deg,#db2777,#be185d)",i:"⏰"}].map(function(k){return'<div class="kpi" style="background:'+k.bg+'"><div class="kpi-icon">'+k.i+'</div><div class="kpi-label">'+k.l+'</div><div class="kpi-val">'+k.v+'</div><div class="kpi-sub">'+k.s+'</div></div>';}).join("");
  bc("dash-chart","dash-labels",gmd(6),135);
  var rec=DB.transactions.slice().sort(function(a,b){return b.date.localeCompare(a.date);}).slice(0,6);
  gi("recent-list").innerHTML=rec.length===0?'<div class="empty">暂无收支记录</div>':rec.map(function(t){return'<div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #f8fafc"><div><div style="font-size:13px;font-weight:500;color:#334155">'+esc(t.category)+'</div><div style="font-size:11px;color:#94a3b8">'+esc(t.date)+' · '+esc(t.method)+'</div></div><div style="font-size:13px;font-weight:700;color:'+(t.type==="income"?"#16a34a":"#dc2626")+';white-space:nowrap;margin-left:7px">'+(t.type==="income"?"+":"−")+fm(t.amount)+'</div></div>';}).join("");
  var low=DB.inventory.filter(function(i){return i.quantity<=5;});
  var lw=gi("low-stock-wrap");
  if(low.length===0){lw.innerHTML="";return;}
  lw.innerHTML='<div class="alert-box"><div style="font-weight:600;color:#dc2626;font-size:13px;margin-bottom:8px">⚠ 库存预警（≤5件）</div><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(135px,1fr));gap:8px">'+low.map(function(i){return'<div class="stock-card"><div style="font-weight:600;font-size:13px;color:#1e293b">'+esc(i.name)+'</div>'+(i.spec?'<div style="font-size:11px;color:#94a3b8">'+esc(i.spec)+'</div>':"")+'<div style="font-size:17px;font-weight:700;color:'+(i.quantity===0?"#dc2626":"#ea580c")+';margin-top:3px">'+i.quantity+'<span style="font-size:11px;font-weight:400">'+esc(i.unit)+'</span></div></div>';}).join("")+'</div></div>';
}

var _tt="income";
function setTT(t){_tt=t;gi("tb-inc").style.cssText="background:"+(t==="income"?"#16a34a":"#fff")+";color:"+(t==="income"?"#fff":"#64748b")+";border-color:"+(t==="income"?"#16a34a":"#e2e8f0");gi("tb-exp").style.cssText="background:"+(t==="expense"?"#dc2626":"#fff")+";color:"+(t==="expense"?"#fff":"#64748b")+";border-color:"+(t==="expense"?"#dc2626":"#e2e8f0");gi("f-cat").innerHTML=(t==="income"?INC_CATS:EXP_CATS).map(function(c){return'<option>'+c+'</option>';}).join("");}
function openTxnModal(){setTT("income");gi("f-amt").value="";gi("f-date").value=today();gi("f-desc").value="";openM("m-txn");}
function saveTxn(){var amt=parseFloat(gi("f-amt").value);if(!amt||amt<=0){alert("请输入有效金额");return;}DB.transactions.push({id:genId(),type:_tt,amount:amt,category:gi("f-cat").value,date:gi("f-date").value,method:gi("f-method").value,description:gi("f-desc").value});save();closeM("m-txn");rTxn();}
function rTxn(){
  var ft=gi("ft-type").value,fm2=gi("ft-month").value;
  var list=DB.transactions.filter(function(t){return(ft==="all"||t.type===ft)&&(!fm2||t.date.indexOf(fm2)===0);}).sort(function(a,b){return b.date.localeCompare(a.date);});
  var inc=list.filter(function(t){return t.type==="income";}).reduce(function(s,t){return s+t.amount;},0);
  var exp=list.filter(function(t){return t.type==="expense";}).reduce(function(s,t){return s+t.amount;},0);
  gi("txn-stats").innerHTML='<div class="stat-chip"><span class="sc-label">收入</span><span class="sc-val" style="color:#16a34a">'+fm(inc)+'</span></div><div class="stat-chip"><span class="sc-label">支出</span><span class="sc-val" style="color:#dc2626">'+fm(exp)+'</span></div><div class="stat-chip"><span class="sc-label">净额</span><span class="sc-val" style="color:'+(inc-exp>=0?"#2563eb":"#dc2626")+'">'+fm(inc-exp)+'</span></div>';
  gi("txn-body").innerHTML=list.length===0?'<tr><td colspan="7" class="empty">暂无记录</td></tr>':list.map(function(t){return'<tr><td style="color:#94a3b8;font-size:12px">'+esc(t.date)+'</td><td><span class="badge '+(t.type==="income"?"b-income":"b-expense")+'">'+(t.type==="income"?"收入":"支出")+'</span></td><td style="font-weight:500">'+esc(t.category)+'</td><td style="color:#94a3b8">'+esc(t.description||"—")+'</td><td style="color:#94a3b8">'+esc(t.method)+'</td><td class="r" style="font-weight:700;color:'+(t.type==="income"?"#16a34a":"#dc2626")+'">'+(t.type==="income"?"+":"−")+fm(t.amount)+'</td><td style="text-align:center"><button class="btn-sm btn-red" onclick="delTxn(\''+t.id+'\')">删除</button></td></tr>';}).join("");
}
function delTxn(id){if(!confirm("确认删除？"))return;DB.transactions=DB.transactions.filter(function(t){return t.id!==id;});save();rTxn();}

function openInvModal(id){gi("inv-title").textContent=id?"编辑商品":"新增商品";gi("inv-btn").textContent=id?"保存修改":"确认添加";gi("i-eid").value=id||"";if(id){var it=DB.inventory.filter(function(x){return x.id===id;})[0];gi("i-name").value=it.name;gi("i-spec").value=it.spec||"";gi("i-sup").value=it.supplier||"";gi("i-buy").value=it.purchase_price;gi("i-sell").value=it.selling_price||"";gi("i-qty").value=it.quantity;gi("i-unit").value=it.unit;}else{["i-name","i-spec","i-sup","i-buy","i-sell","i-qty"].forEach(function(x){gi(x).value="";});gi("i-unit").value="件";}openM("m-inv");}
function saveInv(){var name=gi("i-name").value.trim(),buy=parseFloat(gi("i-buy").value);if(!name||!buy){alert("请填写商品名称和进价");return;}var eid=gi("i-eid").value;var obj={name:name,spec:gi("i-spec").value,supplier:gi("i-sup").value,purchase_price:buy,selling_price:parseFloat(gi("i-sell").value)||0,quantity:parseFloat(gi("i-qty").value)||0,unit:gi("i-unit").value};if(eid){DB.inventory=DB.inventory.map(function(x){return x.id===eid?Object.assign({},obj,{id:eid}):x;});}else{obj.id=genId();DB.inventory.push(obj);}save();closeM("m-inv");rInv();}
function adjQty(id,d){DB.inventory=DB.inventory.map(function(i){return i.id===id?Object.assign({},i,{quantity:Math.max(0,i.quantity+d)}):i;});save();rInv();}
function delInv(id){if(!confirm("确认删除？"))return;DB.inventory=DB.inventory.filter(function(i){return i.id!==id;});save();rInv();}
function rInv(){
  var q=(gi("inv-search").value||"").toLowerCase();
  var list=DB.inventory.filter(function(i){return!q||(i.name+i.spec+(i.supplier||"")).toLowerCase().indexOf(q)>=0;});
  var tv=DB.inventory.reduce(function(s,i){return s+i.purchase_price*i.quantity;},0);
  gi("inv-stats").innerHTML='<div class="stat-chip"><span class="sc-label">库存总值</span><span class="sc-val" style="color:#7c3aed">'+fm(tv)+'</span></div><div class="stat-chip"><span class="sc-label">种类</span><span class="sc-val" style="color:#059669">'+DB.inventory.length+'种</span></div>';
  gi("inv-body").innerHTML=list.length===0?'<tr><td colspan="9" class="empty">暂无商品</td></tr>':list.map(function(i){var low=i.quantity<=5,mg=i.selling_price>0?((i.selling_price-i.purchase_price)/i.selling_price*100):0;return'<tr><td style="font-weight:600">'+esc(i.name)+(low?'<span class="badge b-warn">'+(i.quantity===0?"缺货":"低库存")+'</span>':"")+' </td><td style="color:#94a3b8">'+esc(i.spec||"—")+'</td><td style="color:#94a3b8">'+esc(i.supplier||"—")+'</td><td class="r">'+fm(i.purchase_price)+'</td><td class="r" style="color:#16a34a;font-weight:500">'+fm(i.selling_price)+'</td><td class="r" style="font-weight:600;color:'+(mg>=20?"#16a34a":mg>=10?"#ea580c":"#dc2626")+'">'+mg.toFixed(1)+'%</td><td class="r"><div class="qty-ctrl"><button class="qty-btn" onclick="adjQty(\''+i.id+'\',-1)">−</button><span style="font-weight:700;min-width:32px;text-align:center;color:'+(low?"#dc2626":"#1e293b")+'">'+i.quantity+esc(i.unit)+'</span><button class="qty-btn" onclick="adjQty(\''+i.id+'\',1)">+</button></div></td><td class="r" style="font-weight:600;color:#7c3aed">'+fm(i.purchase_price*i.quantity)+'</td><td style="text-align:center;white-space:nowrap"><button class="btn-sm btn-blue" style="margin-right:3px" onclick="openInvModal(\''+i.id+'\')">编辑</button><button class="btn-sm btn-red" onclick="delInv(\''+i.id+'\')">删除</button></td></tr>';}).join("");
}

var _at="receivable";
function setAT(t){_at=t;gi("tb-recv").style.cssText="background:"+(t==="receivable"?"#ea580c":"#fff")+";color:"+(t==="receivable"?"#fff":"#64748b")+";border-color:"+(t==="receivable"?"#ea580c":"#e2e8f0");gi("tb-apy").style.cssText="background:"+(t==="payable"?"#db2777":"#fff")+";color:"+(t==="payable"?"#fff":"#64748b")+";border-color:"+(t==="payable"?"#db2777":"#e2e8f0");gi("ar-cl").textContent=t==="receivable"?"客户名称 *":"供应商名称 *";}
function openArapModal(){setAT("receivable");["ar-contact","ar-amt","ar-due","ar-desc"].forEach(function(x){gi(x).value="";});gi("ar-date").value=today();openM("m-arap");}
function saveArap(){var c=gi("ar-contact").value.trim(),a=parseFloat(gi("ar-amt").value);if(!c||!a){alert("请填写联系人和金额");return;}DB.arap.push({id:genId(),type:_at,contact:c,amount:a,date:gi("ar-date").value,due_date:gi("ar-due").value,description:gi("ar-desc").value,paid:0,status:"pending"});save();closeM("m-arap");rArap();}
function rArap(){
  var tAR=DB.arap.filter(function(a){return a.type==="receivable"&&a.status!=="done";}).reduce(function(s,a){return s+(a.amount-(a.paid||0));},0);
  var tAP=DB.arap.filter(function(a){return a.type==="payable"&&a.status!=="done";}).reduce(function(s,a){return s+(a.amount-(a.paid||0));},0);
  var od=DB.arap.filter(function(a){return a.status!=="done"&&a.due_date&&a.due_date<today();}).length;
  gi("arap-stats").innerHTML='<div class="stat-chip"><span class="sc-label">待收款</span><span class="sc-val" style="color:#ea580c">'+fm(tAR)+'</span></div><div class="stat-chip"><span class="sc-label">待付款</span><span class="sc-val" style="color:#db2777">'+fm(tAP)+'</span></div>'+(od>0?'<div class="stat-chip"><span class="sc-label">逾期</span><span class="sc-val" style="color:#dc2626">'+od+'笔</span></div>':"");
  var list=DB.arap.filter(function(a){if(_af==="receivable")return a.type==="receivable";if(_af==="payable")return a.type==="payable";if(_af==="pending")return a.status!=="done";if(_af==="overdue")return a.status!=="done"&&a.due_date&&a.due_date<today();return true;}).sort(function(a,b){return b.date.localeCompare(a.date);});
  gi("arap-body").innerHTML=list.length===0?'<tr><td colspan="9" class="empty">暂无账款记录</td></tr>':list.map(function(a){var rem=a.amount-(a.paid||0),ov=a.due_date&&a.due_date<today()&&a.status!=="done";return'<tr class="'+(ov?"overdue-row":"")+'"><td style="font-weight:600">'+esc(a.contact)+(ov?'<span class="badge b-warn">逾期</span>':"")+' </td><td><span class="badge '+(a.type==="receivable"?"b-recv":"b-pay")+'">'+(a.type==="receivable"?"应收":"应付")+'</span></td><td style="color:#94a3b8">'+esc(a.description||"—")+'</td><td style="color:#94a3b8;font-size:12px">'+esc(a.date)+'</td><td style="color:'+(ov?"#dc2626":"#94a3b8")+';font-size:12px">'+esc(a.due_date||"—")+'</td><td class="r">'+fm(a.amount)+'</td><td class="r" style="font-weight:700;color:'+(rem>0?"#dc2626":"#16a34a")+'">'+fm(rem)+'</td><td><span class="badge '+(a.status==="done"?"b-done":a.status==="partial"?"b-partial":"b-pending")+'">'+(a.status==="done"?"已结清":a.status==="partial"?"部分付款":"待结清")+'</span></td><td style="text-align:center;white-space:nowrap">'+(a.status!=="done"?'<button class="btn-sm btn-blue" style="margin-right:3px" onclick="openPayModal(\''+a.id+'\')">收/付款</button>':"")+'<button class="btn-sm btn-red" onclick="delArap(\''+a.id+'\')">删除</button></td></tr>';}).join("");
}
function delArap(id){if(!confirm("确认删除？"))return;DB.arap=DB.arap.filter(function(a){return a.id!==id;});save();rArap();}
var _pid=null;
function openPayModal(id){_pid=id;var a=DB.arap.filter(function(x){return x.id===id;})[0];var rem=a.amount-(a.paid||0);var isR=a.type==="receivable";gi("pay-title").textContent=(isR?"收款":"付款")+"登记 · "+a.contact;gi("pay-lbl").textContent="本次"+(isR?"收款":"付款")+"金额（元）";gi("pay-amt").value="";gi("pay-amt").placeholder="最多 "+rem.toFixed(2);gi("pay-info").innerHTML='<div class="info-row"><span>账款总额</span><span>'+fm(a.amount)+'</span></div><div class="info-row"><span>已'+(isR?"收":"付")+'</span><span style="color:#16a34a">'+fm(a.paid||0)+'</span></div><div style="border-top:1px dashed #e2e8f0;margin:7px 0"></div><div class="info-row"><span>待结清</span><span style="color:#dc2626;font-size:15px;font-weight:700">'+fm(rem)+'</span></div>';openM("m-pay");}
function setFullPay(){var a=DB.arap.filter(function(x){return x.id===_pid;})[0];gi("pay-amt").value=(a.amount-(a.paid||0)).toFixed(2);}
function confirmPay(){var amt=parseFloat(gi("pay-amt").value);if(!amt||amt<=0){alert("请输入金额");return;}DB.arap=DB.arap.map(function(a){if(a.id!==_pid)return a;var np=Math.min((a.paid||0)+amt,a.amount);return Object.assign({},a,{paid:np,status:a.amount-np<=0?"done":"partial"});});save();closeM("m-pay");rArap();}

function rRpt(){
  var rM=gi("rpt-month").value||nowM();gi("rpt-month").value=rM;
  var mT=DB.transactions.filter(function(t){return t.date.indexOf(rM)===0;});
  var mI=mT.filter(function(t){return t.type==="income";}).reduce(function(s,t){return s+t.amount;},0);
  var mE=mT.filter(function(t){return t.type==="expense";}).reduce(function(s,t){return s+t.amount;},0);
  var mP=mI-mE,mg=mI>0?(mP/mI*100):0;
  gi("rpt-kpi").innerHTML=[{l:"月度收入",v:fm(mI),s:"本月收入",bg:"linear-gradient(135deg,#16a34a,#15803d)",i:"↑"},{l:"月度支出",v:fm(mE),s:"本月支出",bg:"linear-gradient(135deg,#dc2626,#b91c1c)",i:"↓"},{l:"净利润",v:fm(mP),s:mP>=0?"盈利":"亏损",bg:mP>=0?"linear-gradient(135deg,#2563eb,#1d4ed8)":"linear-gradient(135deg,#dc2626,#b91c1c)",i:"="},{l:"毛利率",v:mg.toFixed(1)+"%",s:mg>=20?"健康":mg>=10?"尚可":"偏低",bg:"linear-gradient(135deg,#0891b2,#0e7490)",i:"≈"}].map(function(k){return'<div class="kpi" style="background:'+k.bg+'"><div class="kpi-icon">'+k.i+'</div><div class="kpi-label">'+k.l+'</div><div class="kpi-val">'+k.v+'</div><div class="kpi-sub">'+k.s+'</div></div>';}).join("");
  bc("rpt-chart","rpt-labels",gmd(12),175);
  function mkPie(type,elId){var ts=DB.transactions.filter(function(t){return t.type===type&&t.date.indexOf(rM)===0;});var map={};ts.forEach(function(t){map[t.category]=(map[t.category]||0)+t.amount;});var items=Object.entries(map).sort(function(a,b){return b[1]-a[1];});var total=items.reduce(function(s,x){return s+x[1];},0);var el=gi(elId);if(items.length===0){el.innerHTML='<div class="empty">本月暂无数据</div>';return;}el.innerHTML=items.map(function(x,i){var pct=total>0?Math.round(x[1]/total*100):0;return'<div class="pie-item"><div class="pie-dot" style="background:'+PAL[i%PAL.length]+'"></div><span style="min-width:54px;color:#475569">'+esc(x[0])+'</span><div class="pie-bar-bg"><div class="pie-bar-fill" style="width:'+pct+'%;background:'+PAL[i%PAL.length]+'"></div></div><div class="pie-val">'+fm(x[1])+'</div></div>';}).join("");}
  mkPie("income","inc-pie");mkPie("expense","exp-pie");
  var mgs=DB.inventory.filter(function(i){return i.selling_price>i.purchase_price;}).map(function(i){return{n:i.name+(i.spec?" ("+i.spec+")":""),v:i.selling_price-i.purchase_price};}).sort(function(a,b){return b.v-a.v;}).slice(0,8);
  var mc=gi("mg-card");if(mgs.length===0){mc.style.display="none";return;}mc.style.display="block";
  var maxM=Math.max.apply(null,mgs.map(function(x){return x.v;}));
  gi("mg-chart").innerHTML=mgs.map(function(x,i){return'<div class="mg-row"><div class="mg-name" title="'+esc(x.n)+'">'+esc(x.n)+'</div><div class="mg-bar-bg"><div class="mg-bar-fill" style="width:'+Math.round(x.v/maxM*100)+'%;background:'+PAL[i%PAL.length]+'"></div></div><div class="mg-val">'+fm(x.v)+'</div></div>';}).join("");
}
</script>
</body>
</html>`;

const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://localhost');
  const pathname = url.pathname;

  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, x-password');
  if (req.method === 'OPTIONS') { res.writeHead(200); res.end(); return; }

  if (pathname === '/api/ping') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ ok: true }));
    return;
  }

  if (pathname === '/api/login' && req.method === 'POST') {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', () => {
      try {
        const { password } = JSON.parse(body);
        if (password === PASSWORD) {
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ ok: true }));
        } else {
          res.writeHead(401, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ ok: false }));
        }
      } catch(e) {
        res.writeHead(400); res.end('{}');
      }
    });
    return;
  }

  if (pathname === '/api/data') {
    const pwd = req.headers['x-password'];
    if (pwd !== PASSWORD) { res.writeHead(401); res.end('{}'); return; }

    if (req.method === 'GET') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(readDB()));
      return;
    }
    if (req.method === 'POST') {
      let body = '';
      req.on('data', c => body += c);
      req.on('end', () => {
        try { writeDB(JSON.parse(body)); } catch(e) {}
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ ok: true }));
      });
      return;
    }
  }

  // 默认返回 HTML
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(HTML);
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log('运行在 http://localhost:' + PORT));
module.exports = server;
