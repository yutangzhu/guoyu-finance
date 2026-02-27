# -*- coding: utf-8 -*-
"""
国宇制冷理财管家 - 管家婆风格：多账户、应收应付、转账、资产负债
"""
import sys
import streamlit as st
import pandas as pd
from datetime import datetime
import json
from pathlib import Path

# ================= 配置 =================
# 打包成单文件 exe 时，数据放在 exe 所在目录，便于持久化；否则放在本脚本同目录
if getattr(sys, "frozen", False):
    DATA_DIR = Path(sys.executable).parent / "data"
else:
    DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
TRANSACTIONS_FILE = DATA_DIR / "transactions.json"
BUDGETS_FILE = DATA_DIR / "budgets.json"
CATEGORIES_FILE = DATA_DIR / "categories.json"
ACCOUNTS_FILE = DATA_DIR / "accounts.json"
DEBT_FILE = DATA_DIR / "debt.json"
DELIVERY_NOTES_FILE = DATA_DIR / "delivery_notes.json"
COMPANY_FILE = DATA_DIR / "company.json"
PRODUCTS_FILE = DATA_DIR / "products.json"
PAYMENTS_FILE = DATA_DIR / "payments.json"  # 客户收款记录

# 财务云结构新增：销货单 / 购货单 / 库存 / 往来流水
SALES_HEADER_FILE = DATA_DIR / "sales_header.json"
SALES_DETAIL_FILE = DATA_DIR / "sales_detail.json"
PURCHASE_HEADER_FILE = DATA_DIR / "purchase_header.json"
PURCHASE_DETAIL_FILE = DATA_DIR / "purchase_detail.json"
STOCK_MOVES_FILE = DATA_DIR / "stock_moves.json"
ARAP_MOVES_FILE = DATA_DIR / "arap_moves.json"

DEFAULT_INCOME_CATS = ["工资", "奖金", "投资收益", "兼职", "其他收入"]
DEFAULT_EXPENSE_CATS = ["餐饮", "交通", "住房", "购物", "娱乐", "医疗", "教育", "通讯", "其他支出"]
DEFAULT_ACCOUNTS = [
    {"id": 1, "name": "现金", "type": "现金", "init_balance": 0},
    {"id": 2, "name": "银行卡", "type": "银行卡", "init_balance": 0},
    {"id": 3, "name": "支付宝", "type": "支付宝", "init_balance": 0},
    {"id": 4, "name": "微信", "type": "微信", "init_balance": 0},
]


# ================= 数据操作 =================
def load_json(path, default):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default.copy() if isinstance(default, (list, dict)) else default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_transactions():
    return load_json(TRANSACTIONS_FILE, [])


def save_transactions(data):
    save_json(TRANSACTIONS_FILE, data)


def load_budgets():
    return load_json(BUDGETS_FILE, {})


def load_categories():
    cats = load_json(CATEGORIES_FILE, {"income": DEFAULT_INCOME_CATS, "expense": DEFAULT_EXPENSE_CATS})
    if "income" not in cats:
        cats["income"] = DEFAULT_INCOME_CATS
    if "expense" not in cats:
        cats["expense"] = DEFAULT_EXPENSE_CATS
    return cats


def save_categories(data):
    save_json(CATEGORIES_FILE, data)


def load_accounts():
    acc = load_json(ACCOUNTS_FILE, DEFAULT_ACCOUNTS)
    if not acc:
        return DEFAULT_ACCOUNTS.copy()
    return acc


def save_accounts(data):
    save_json(ACCOUNTS_FILE, data)


def load_debt():
    return load_json(DEBT_FILE, [])


def save_debt(data):
    save_json(DEBT_FILE, data)


def load_delivery_notes():
    return load_json(DELIVERY_NOTES_FILE, [])


def save_delivery_notes(data):
    save_json(DELIVERY_NOTES_FILE, data)


def load_company():
    return load_json(COMPANY_FILE, {
        "name": "国宇制冷",
        "title": "销售出库单",
        "business_scope": "JDG铁管及辅件,PVC红蓝白线管,线管及辅件,旋流消音管件,及农田灌溉及辅件",
        "contact_phones": "15333773152 61155122",
        "default_handler": "安然",
        "default_preparer": "安然",
    })


def save_company(data):
    save_json(COMPANY_FILE, data)


def load_products():
    return load_json(PRODUCTS_FILE, [])


def save_products(data):
    save_json(PRODUCTS_FILE, data)


def load_payments():
    return load_json(PAYMENTS_FILE, [])


def save_payments(data):
    save_json(PAYMENTS_FILE, data)


# 商品名称/单价的常见 Excel 列名
PRODUCT_NAME_ALIASES = ["商品名称", "名称", "品名", "货品名称", "商品", "品名规格"]
UNIT_PRICE_ALIASES = ["单价", "价格", "单位价格", "零售价", "售价", "含税价"]


def _find_column(df_columns, aliases):
    """在 DataFrame 列名中查找第一个匹配的列"""
    cols = [str(c).strip() for c in df_columns]
    for a in aliases:
        for i, c in enumerate(cols):
            if a in c or c in a:
                return df_columns[i]
    return None


def import_products_from_excel(file_or_path, products, merge=True):
    """
    从 Excel 文件导入商品到商品库。
    file_or_path: 上传的 BytesIO 或本地路径字符串
    products: 当前商品列表（会被原地更新）
    merge: True=同名更新单价，False=仅追加新名称
    返回 (导入条数, 更新条数)
    """
    try:
        import pandas as pd
    except ImportError:
        return 0, 0, "请先安装 pandas: pip install pandas"
    engine = None
    if hasattr(file_or_path, "read"):
        buf = file_or_path
        try:
            import io
            df = pd.read_excel(buf, engine="xlrd")
            engine = "xlrd"
        except Exception:
            buf.seek(0)
            try:
                df = pd.read_excel(buf, engine="openpyxl")
                engine = "openpyxl"
            except Exception as e:
                return 0, 0, f"无法解析 Excel，请确保为 .xls 或 .xlsx。错误: {e}"
    else:
        path = str(file_or_path)
        if path.lower().endswith(".xls"):
            try:
                df = pd.read_excel(path, engine="xlrd")
                engine = "xlrd"
            except ImportError:
                return 0, 0, "读取 .xls 需要安装 xlrd: pip install xlrd"
            except Exception as e:
                return 0, 0, str(e)
        else:
            try:
                df = pd.read_excel(path, engine="openpyxl")
                engine = "openpyxl"
            except ImportError:
                return 0, 0, "读取 .xlsx 需要安装 openpyxl: pip install openpyxl"
            except Exception as e:
                return 0, 0, str(e)
    if df.empty:
        return 0, 0, "文件中没有数据"
    name_col = _find_column(df.columns, PRODUCT_NAME_ALIASES)
    price_col = _find_column(df.columns, UNIT_PRICE_ALIASES)
    if name_col is None:
        return 0, 0, f"未识别到商品名称列，当前列: {list(df.columns)}"
    name_to_price = {}
    for _, row in df.iterrows():
        name = str(row.get(name_col, "") or "").strip()
        if not name or name == "nan":
            continue
        if price_col is not None:
            try:
                p = float(row.get(price_col, 0) or 0)
            except (TypeError, ValueError):
                p = 0
        else:
            p = 0
        name_to_price[name] = p
    imported, updated = 0, 0
    products_by_name = {str(p.get("name", "")).strip(): p for p in products}
    for name, price in name_to_price.items():
        if name in products_by_name:
            if merge:
                products_by_name[name]["unit_price"] = price
                updated += 1
        else:
            products.append({"name": name, "unit_price": price})
            products_by_name[name] = products[-1]
            imported += 1
    save_products(products)
    return imported, updated, None


def next_id(items, key="id"):
    return max([x.get(key, 0) for x in items], default=0) + 1


# ================= 账户余额计算 =================
def calc_account_balance(account_id, transactions, accounts):
    acc = next((a for a in accounts if a["id"] == account_id), None)
    if not acc:
        return 0
    balance = float(acc.get("init_balance", 0))
    default_acc = accounts[0]["id"] if accounts else None
    for t in transactions:
        t_type = t.get("type", "")
        acc_id = t.get("account_id") or t.get("account")
        if acc_id is None and t_type in ("收入", "支出"):
            acc_id = default_acc
        from_id = t.get("from_account_id")
        to_id = t.get("to_account_id")
        amt = float(t.get("amount", 0))
        if t_type == "收入" and acc_id == account_id:
            balance += amt
        elif t_type == "支出" and acc_id == account_id:
            balance -= amt
        elif t_type == "转账":
            if from_id == account_id:
                balance -= amt
            elif to_id == account_id:
                balance += amt
        elif t_type in ("借出", "还出") and acc_id == account_id:
            balance -= amt
        elif t_type in ("借入", "还入") and acc_id == account_id:
            balance += amt
    return balance


# ================= 应收应付汇总 =================
def calc_debt_summary(debt_records):
    receivables = {}  # 别人欠我
    payables = {}    # 我欠别人
    for d in debt_records:
        person = d.get("contact", d.get("person", ""))
        amt = float(d.get("amount", 0))
        t = d.get("type", "")
        if t == "借出":
            receivables[person] = receivables.get(person, 0) + amt
        elif t == "还入":
            receivables[person] = receivables.get(person, 0) - amt
        elif t == "借入":
            payables[person] = payables.get(person, 0) + amt
        elif t == "还出":
            payables[person] = payables.get(person, 0) - amt
    return {k: v for k, v in receivables.items() if v > 0}, {k: v for k, v in payables.items() if v > 0}


def build_receipt_html(company, record_date, handler, number, summary, buyer, buyer_phone, lines, discount, total, preparer):
    """生成销售出库单 HTML，用于打印或下载"""
    def esc(s):
        if s is None:
            return ""
        return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    company_name = esc(company.get("name", ""))
    title = esc(company.get("title", "销售出库单"))
    business_scope = esc(company.get("business_scope", ""))
    contact_phones = esc(company.get("contact_phones", ""))
    rows = ""
    for i, line in enumerate(lines, 1):
        name = esc(line.get("product_name", line.get("商品名称", "")))
        qty = line.get("quantity", line.get("数量", 0))
        try:
            qty = float(qty)
        except (TypeError, ValueError):
            qty = 0
        price = line.get("unit_price", line.get("单价", 0))
        try:
            price = float(price)
        except (TypeError, ValueError):
            price = 0
        amount = qty * price
        remark = esc(line.get("remark", line.get("备注", "")))
        rows += f"<tr><td>{i}</td><td>{name}</td><td>{qty}</td><td>{price}</td><td>{amount:.2f}</td><td>{remark}</td></tr>"
    try:
        disc = float(discount) if discount not in (None, "") else 0
    except (TypeError, ValueError):
        disc = 0
    if isinstance(total, (int, float)):
        total_val = float(total)
    else:
        total_val = 0
        for l in lines:
            q = float(l.get("quantity", l.get("数量", 0)) or 0)
            p = float(l.get("unit_price", l.get("单价", 0)) or 0)
            total_val += q * p
    try:
        total_val = float(total_val) - disc
    except (TypeError, ValueError):
        total_val = 0
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>{company_name}{title}</title>
<style>
body {{ font-family: "Microsoft YaHei", "SimSun", sans-serif; margin: 20px; }}
h1 {{ text-align: center; font-size: 22px; margin-bottom: 16px; }}
table {{ width: 100%; border-collapse: collapse; margin: 12px 0; }}
th, td {{ border: 1px solid #333; padding: 6px 8px; text-align: left; }}
th {{ background: #f0f0f0; }}
.info {{ display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 14px; }}
.footer {{ display: flex; justify-content: space-between; margin-top: 12px; font-size: 14px; }}
.main {{ font-size: 13px; }}
@media print {{ body {{ margin: 0; }} }}
</style></head><body>
<h1>{company_name}{title}</h1>
<div class="info">
  <span>录单日期: {esc(record_date)}</span>
  <span>编号: {esc(number)}</span>
  <span>购买单位: {esc(buyer)} {esc(buyer_phone)}</span>
</div>
<div class="info">
  <span>经手人: {esc(handler)}</span>
  <span>摘要: {esc(summary)}</span>
</div>
<table class="main">
  <thead><tr><th>行号</th><th>商品名称</th><th>数量</th><th>单价</th><th>金额</th><th>备注</th></tr></thead>
  <tbody>{rows}</tbody>
</table>
<div class="footer">
  <span>制单人: {esc(preparer)}</span>
  <span>优惠金额: {disc}</span>
  <span>合计金额: {total_val:.2f}</span>
</div>
<div style="margin-top:16px;font-size:12px;color:#555;">
  主营: {business_scope}<br>联系电话: {contact_phones}
</div>
<p style="margin-top:20px;font-size:12px;color:#999;">请按 Ctrl+P 打印或另存为 PDF</p>
</body></html>"""
    return html


# ================= 页面样式（财务云风格，仿迷你云）=================
st.set_page_config(page_title="财务云进销存", page_icon="☁", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');
    .stApp { font-family: 'Noto Sans SC', sans-serif; }
    .miniyun-login-left { background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%); color: #fff; padding: 2rem; border-radius: 12px; }
    .miniyun-login-title { font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem; }
    .miniyun-login-desc { font-size: 0.9rem; opacity: 0.95; margin: 0.5rem 0; }
    .miniyun-stat { display: inline-block; text-align: center; padding: 0.8rem 1rem; margin: 0.3rem; background: rgba(255,255,255,0.15); border-radius: 8px; }
    .miniyun-stat-num { font-size: 1.5rem; font-weight: 700; }
    .miniyun-topbar { background: #1e3a5f; color: #fff; padding: 0.4rem 1rem; border-radius: 6px; margin-bottom: 1rem; }
    .miniyun-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
    .miniyun-card-title { font-size: 0.85rem; color: #6b7280; margin-bottom: 0.2rem; }
    .miniyun-card-value { font-size: 1.5rem; font-weight: 700; color: #1f2937; }
    .miniyun-shortcut { padding: 1rem; border: 1px solid #e5e7eb; border-radius: 8px; text-align: center; cursor: pointer; transition: all 0.2s; }
    .miniyun-shortcut:hover { border-color: #3b82f6; background: #eff6ff; }
    div[data-testid="stSidebar"] { background: linear-gradient(180deg, #1e3a5f 0%, #16304d 100%); }
    div[data-testid="stSidebar"] .stMarkdown { color: #e5e7eb !important; }
    .main-header { font-size: 1.5rem; font-weight: 700; color: #1a1a2e; margin-bottom: 0.5rem; }
    .sub-header { color: #6b7280; font-size: 0.95rem; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)


# ================= 登录校验（财务云登录页）=================
def _get_login_credentials():
    try:
        u = st.secrets.get("LOGIN_USERNAME", "").strip()
        p = st.secrets.get("LOGIN_PASSWORD", "").strip()
        return (u, p) if (u and p) else (None, None)
    except Exception:
        return (None, None)


if not st.session_state.get("logged_in", False):
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.markdown('<div class="miniyun-login-left">', unsafe_allow_html=True)
        st.markdown("### 财务云 · 进销存")
        st.markdown('<p class="miniyun-login-desc">完美适配中小微企业及迷你型企业的进销存软件</p>', unsafe_allow_html=True)
        st.markdown("多用户 · 多仓库 · 多门店  \n多规格 · 多批次 · 多单位  \n电脑端 · 平板端 · 手机端，多端数据同步", unsafe_allow_html=True)
        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("10年", "行业经验")
        with c2: st.metric("10年", "稳定运营")
        with c3: st.metric("10万+", "在线用户")
        with c4: st.metric("10秒", "极速开单")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_right:
        st.markdown("## 用户登陆")
        username, password = _get_login_credentials()
        if not username or not password:
            st.warning("请在 Streamlit Cloud 的 Advanced settings → Secrets 中配置 **LOGIN_USERNAME** 和 **LOGIN_PASSWORD**。")
        with st.form("login_form"):
            u = st.text_input("账号", placeholder="请输入账号", key="login_user")
            p = st.text_input("密码", type="password", placeholder="请输入密码", key="login_pwd")
            st.checkbox("记住账号", key="remember")
            submitted = st.form_submit_button("登 陆")
        if submitted:
            if not username or not password:
                st.error("当前未配置账号密码，无法登录。")
            elif u == username and p == password:
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("账号或密码错误。")
    st.caption("© 财务云进销存 版权所有")
    st.stop()


# ================= 顶栏（财务云风格）=================
company = load_company()
top1, top2, top3, top4, top5 = st.columns([2, 1, 1, 1, 1])
with top1:
    st.markdown(f"**{company.get('name', '财务云')}**")
with top2:
    st.caption("用户：当前账户")
with top3:
    if st.button("🔄 刷新", key="tb_refresh"):
        st.rerun()
with top4:
    st.caption("授权：迷你版")
with top5:
    if st.button("🚪 退出", key="tb_exit"):
        st.session_state["logged_in"] = False
        st.rerun()
st.markdown("---")

# ================= 侧边栏（财务云：进货/销售/库存/财务/报表/设置）=================
st.sidebar.markdown("### ☁ 财务云")
st.sidebar.markdown("---")
main_nav = st.sidebar.radio(
    "主导航",
    ["首页", "进货", "销售", "库存", "财务", "报表", "设置"],
    label_visibility="collapsed",
    key="main_nav"
)
st.sidebar.markdown("---")

# 子菜单 / 页面映射
page = None
if main_nav == "首页":
    page = "首页"
elif main_nav == "进货":
    page = "进货-购货单"
elif main_nav == "销售":
    sub = st.sidebar.radio("销售", ["销货单", "客户账单"], label_visibility="collapsed", key="sales_sub")
    page = "销售-销货单" if sub == "销货单" else "销售-客户账单"
elif main_nav == "库存":
    page = "库存-库存查询"
elif main_nav == "财务":
    sub = st.sidebar.radio("财务", ["记一笔", "转账", "应收应付", "账户管理", "预算管理"], label_visibility="collapsed", key="finance_sub")
    page = {"记一笔": "➕ 记一笔", "转账": "🔄 转账", "应收应付": "📥 应收应付", "账户管理": "🏦 账户管理", "预算管理": "📈 预算管理"}[sub]
elif main_nav == "报表":
    sub = st.sidebar.radio("报表", ["总览", "流水记录"], label_visibility="collapsed", key="report_sub")
    page = "📊 总览" if sub == "总览" else "📋 流水记录"
elif main_nav == "设置":
    sub = st.sidebar.radio("设置", ["分类设置", "公司信息", "商品管理"], label_visibility="collapsed", key="setting_sub")
    page = "⚙️ 分类设置" if sub == "分类设置" else ("公司信息" if sub == "公司信息" else "商品管理")

# 将“销售”子菜单映射到原有页面键
if page == "销售-销货单":
    page = "📄 销售出库单"
elif page == "销售-客户账单":
    page = "👤 客户账单"

st.sidebar.markdown("---")
st.sidebar.caption("© 财务云 版权所有")

# ================= 数据加载 =================
transactions = load_transactions()
budgets = load_json(BUDGETS_FILE, {})
categories = load_categories()
accounts = load_accounts()
debt_records = load_debt()
receivables, payables = calc_debt_summary(debt_records)
rec_total = sum(receivables.values())
pay_total = sum(payables.values())
df_tx = pd.DataFrame(transactions)
month_sales = 0
month_purchase = 0
if not df_tx.empty and "date" in df_tx.columns:
    df_tx["date"] = pd.to_datetime(df_tx["date"])
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    df_month = df_tx[df_tx["date"] >= month_start]
    month_sales = df_month[df_month["type"] == "收入"]["amount"].sum() if "type" in df_month.columns else 0
    month_purchase = df_month[df_month["type"] == "支出"]["amount"].sum() if "type" in df_month.columns else 0


def add_transaction(transactions, t_type, amount, category, note, date, account_id=None,
                    from_account_id=None, to_account_id=None):
    tid = next_id(transactions)
    t = {
        "id": tid,
        "type": t_type,
        "amount": float(amount),
        "category": category or "",
        "note": note or "",
        "date": date.strftime("%Y-%m-%d"),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if account_id is not None:
        t["account_id"] = account_id
    if from_account_id is not None:
        t["from_account_id"] = from_account_id
    if to_account_id is not None:
        t["to_account_id"] = to_account_id
    transactions.append(t)
    save_transactions(transactions)


def add_debt_record(records, d_type, contact, amount, account_id, date, note):
    records.append({
        "id": next_id(records),
        "type": d_type,
        "contact": contact,
        "amount": float(amount),
        "account_id": account_id,
        "date": date.strftime("%Y-%m-%d"),
        "note": note or "",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_debt(records)


# ================= 页面：首页（迷你云仪表盘）=================
if page == "首页":
    st.markdown('<p class="main-header">工作台</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">快速入门与数据概览</p>', unsafe_allow_html=True)
    with st.expander("快速入门步骤", expanded=False):
        st.write("第一步：设置 → 商品管理 添加商品")
        st.write("第二步：进货 → 购货单 购货入库")
        st.write("第三步：销售 → 销货单 销售出库")
        st.write("第四步：库存 → 库存查询 查询实时库存")
        st.write("第五步：报表 → 销售利润表 查询销售与利润")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("本月采购", f"¥ {month_purchase:,.2f}", "总金额")
    with c2:
        st.metric("供应商", f"¥ {pay_total:,.2f}", "总欠款")
    with c3:
        st.metric("本月销售", f"¥ {month_sales:,.2f}", "总金额")
    with c4:
        st.metric("客户", f"¥ {rec_total:,.2f}", "总欠款")
    st.markdown("---")
    st.subheader("快捷入口")
    s1, s2, s3 = st.columns(3)
    with s1:
        if st.button("📥 购货入库", use_container_width=True):
            st.session_state["main_nav"] = "进货"
            st.rerun()
        if st.button("📤 销售出库", use_container_width=True):
            st.session_state["main_nav"] = "销售"
            st.rerun()
    with s2:
        if st.button("📋 库存盘点", use_container_width=True):
            st.session_state["main_nav"] = "库存"
            st.rerun()
        if st.button("📦 商品", use_container_width=True):
            st.session_state["main_nav"] = "设置"
            st.rerun()
    with s3:
        if st.button("👤 客户", use_container_width=True):
            st.session_state["main_nav"] = "销售"
            st.rerun()
        if st.button("🏭 供应商", use_container_width=True):
            st.session_state["main_nav"] = "进货"
            st.rerun()
    st.markdown("---")
    st.subheader("近15天数据")
    if not df_tx.empty and "date" in df_tx.columns:
        df_tx["date"] = pd.to_datetime(df_tx["date"])
        df_15 = df_tx[df_tx["date"] >= (datetime.now() - pd.Timedelta(days=15))]
        if not df_15.empty:
            df_15["amount"] = df_15.apply(lambda r: r["amount"] if r.get("type") == "收入" else -r["amount"], axis=1)
            daily = df_15.groupby(df_15["date"].dt.date)["amount"].sum().reset_index()
            daily.columns = ["日期", "金额"]
            import plotly.express as px
            fig = px.bar(daily, x="日期", y="金额", color="金额", color_continuous_scale=["#eb3349", "#38ef7d"])
            fig.update_layout(height=280, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无近15天流水。")
    else:
        st.info("暂无流水数据。")

# ================= 页面：进货-购货单 =================
elif page == "进货-购货单":
    st.markdown('<p class="main-header">购货单</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">从供应商进货入库，形成库存与应付款</p>', unsafe_allow_html=True)

    # 读取已有购货单
    purchase_headers = load_json(PURCHASE_HEADER_FILE, [])
    purchase_details = load_json(PURCHASE_DETAIL_FILE, [])

    company = load_company()

    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    same_day = [h for h in purchase_headers if (h.get("biz_date") or "").startswith(today_str)]
    next_seq = len(same_day) + 1
    default_number = f"CG-{now.strftime('%Y%m%d')}-{next_seq:03d}"

    st.subheader("填写购货单")
    col1, col2, col3 = st.columns(3)
    with col1:
        biz_date = st.text_input("业务日期", value=today_str, key="cg_date")
        supplier = st.text_input("供应商", value="", key="cg_supplier")
        warehouse_id = st.text_input("仓库", value="默认仓库", key="cg_wh")
    with col2:
        handler = st.text_input("经手人", value=company.get("default_handler", ""), key="cg_handler")
        summary = st.text_input("摘要", value="", key="cg_summary")
        discount = st.number_input("整单优惠", value=0.0, min_value=0.0, step=0.01, format="%.2f", key="cg_discount")
    with col3:
        number = st.text_input("编号", value=default_number, key="cg_no")
        contact_phone = st.text_input("联系电话", value="", key="cg_phone")
        account_id = st.text_input("本次付款账户", value="", key="cg_account")

    # 明细表
    if "cg_lines" not in st.session_state:
        st.session_state.cg_lines = pd.DataFrame({
            "商品名称": ["", "", ""],
            "数量": [0.0, 0.0, 0.0],
            "单价": [0.0, 0.0, 0.0],
            "备注": ["", "", ""],
        })

    edited = st.data_editor(
        st.session_state.cg_lines,
        column_config={
            "商品名称": st.column_config.TextColumn("商品名称", width="large"),
            "数量": st.column_config.NumberColumn("数量", min_value=0.0, step=0.1, format="%.2f"),
            "单价": st.column_config.NumberColumn("单价", min_value=0.0, step=0.01, format="%.2f"),
            "备注": st.column_config.TextColumn("备注", width="medium"),
        },
        num_rows="dynamic",
        key="cg_lines_editor",
    )
    st.session_state.cg_lines = edited

    edited["金额"] = (edited["数量"].fillna(0) * edited["单价"].fillna(0)).round(2)
    subtotal = float(edited["金额"].sum())
    total = subtotal - float(discount)
    st.caption(f"明细小计: ¥{subtotal:.2f} － 优惠: ¥{float(discount):.2f} ＝ 应付: ¥{total:.2f}")

    col_save, _, _ = st.columns([1, 1, 2])
    with col_save:
        if st.button("保存购货单"):
            lines_raw = edited.drop(columns=["金额"], errors="ignore")
            lines_raw = lines_raw[lines_raw["商品名称"].astype(str).str.strip() != ""]
            if lines_raw.empty:
                st.error("请至少填写一行商品。")
            else:
                # 写入 purchase_header / purchase_detail
                header_id = f"CG{biz_date.replace('-', '')}-{len(purchase_headers)+1:03d}"
                supplier_id = supplier or "S_TMP"
                header = {
                    "id": header_id,
                    "no": number,
                    "biz_date": biz_date,
                    "supplier_id": supplier_id,
                    "warehouse_id": warehouse_id or "W01",
                    "settle_account_id": account_id or None,
                    "amount_total": subtotal,
                    "discount_total": float(discount),
                    "amount_payable": total,
                    "amount_paid": 0.0,
                    "amount_ap": total,
                    "status": "checked",
                    "handler": handler,
                    "summary": summary,
                    "contact_phone": contact_phone,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                purchase_headers.append(header)

                stock_moves = load_json(STOCK_MOVES_FILE, [])
                arap_moves = load_json(ARAP_MOVES_FILE, [])

                line_idx = 1
                for _, row in lines_raw.iterrows():
                    detail_id = f"{header_id}-{line_idx:02d}"
                    line_idx += 1
                    qty = float(row.get("数量", 0) or 0)
                    price = float(row.get("单价", 0) or 0)
                    amount = qty * price
                    goods_id = str(row.get("商品名称", ""))

                    purchase_details.append({
                        "id": detail_id,
                        "header_id": header_id,
                        "goods_id": goods_id,
                        "warehouse_id": warehouse_id or "W01",
                        "qty": qty,
                        "unit": "",
                        "price": price,
                        "discount_rate": 0.0,
                        "tax_rate": 0.0,
                        "amount": amount,
                        "note": str(row.get("备注", "")),
                    })

                    stock_moves.append({
                        "id": detail_id,
                        "biz_date": biz_date,
                        "bill_type": "purchase",
                        "bill_no": number,
                        "goods_id": goods_id,
                        "warehouse_id": warehouse_id or "W01",
                        "qty_in": qty,
                        "qty_out": 0.0,
                        "cost_price": price,
                        "amount_cost": amount,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    })

                arap_moves.append({
                    "id": header_id,
                    "biz_date": biz_date,
                    "obj_type": "supplier",
                    "obj_id": supplier_id,
                    "bill_type": "purchase",
                    "bill_no": number,
                    "debit": 0.0,
                    "credit": total,
                    "note": summary,
                })

                save_json(PURCHASE_HEADER_FILE, purchase_headers)
                save_json(PURCHASE_DETAIL_FILE, purchase_details)
                save_json(STOCK_MOVES_FILE, stock_moves)
                save_json(ARAP_MOVES_FILE, arap_moves)

                st.success("已保存购货单，并写入入库/应付结构")

# ================= 页面：库存-库存查询 =================
elif page == "库存-库存查询":
    st.markdown('<p class="main-header">库存查询</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">按照商品和仓库查看当前库存数量与成本</p>', unsafe_allow_html=True)

    stock_moves = load_json(STOCK_MOVES_FILE, [])
    if not stock_moves:
        st.info("暂无库存数据。请先在【进货 → 购货单】或【销售 → 销货单】中产生单据。")
    else:
        df = pd.DataFrame(stock_moves)

        # 只保留必要字段，计算结存数量和金额
        df["qty_in"] = df.get("qty_in", 0).fillna(0).astype(float)
        df["qty_out"] = df.get("qty_out", 0).fillna(0).astype(float)
        df["amount_cost"] = df.get("amount_cost", 0).fillna(0).astype(float)
        df["qty"] = df["qty_in"] - df["qty_out"]

        if df.empty:
            st.info("暂无库存数据。")
        else:
            grouped = df.groupby(["goods_id", "warehouse_id"], as_index=False).agg(
                qty=("qty", "sum"),
                amount_cost=("amount_cost", "sum"),
            )
            grouped["cost_price"] = grouped.apply(
                lambda r: (r["amount_cost"] / r["qty"]) if r["qty"] else 0.0, axis=1
            )

            col1, col2 = st.columns(2)
            with col1:
                kw = st.text_input("商品关键字", placeholder="按商品名称包含过滤，如：管")
            with col2:
                wh = st.text_input("仓库关键字", placeholder="按仓库名称包含过滤")

            if kw.strip():
                grouped = grouped[grouped["goods_id"].astype(str).str.contains(kw.strip())]
            if wh.strip():
                grouped = grouped[grouped["warehouse_id"].astype(str).str.contains(wh.strip())]

            grouped = grouped.sort_values(["goods_id", "warehouse_id"])
            grouped_display = grouped.rename(
                columns={
                    "goods_id": "商品",
                    "warehouse_id": "仓库",
                    "qty": "数量",
                    "cost_price": "成本单价",
                    "amount_cost": "成本金额",
                }
            )
            st.dataframe(grouped_display, use_container_width=True, hide_index=True)

# ================= 页面：公司信息 =================
elif page == "公司信息":
    st.markdown('<p class="main-header">公司信息</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">用于单据说头与表尾</p>', unsafe_allow_html=True)
    company = load_company()
    with st.form("company_form"):
        c_name = st.text_input("公司名称", value=company.get("name", ""))
        c_title = st.text_input("单据说头", value=company.get("title", "销售出库单"))
        c_scope = st.text_input("主营", value=company.get("business_scope", ""))
        c_phones = st.text_input("联系电话", value=company.get("contact_phones", ""))
        c_handler = st.text_input("默认经手人", value=company.get("default_handler", ""))
        c_preparer = st.text_input("默认制单人", value=company.get("default_preparer", ""))
        if st.form_submit_button("保存"):
            save_company({"name": c_name, "title": c_title, "business_scope": c_scope, "contact_phones": c_phones, "default_handler": c_handler, "default_preparer": c_preparer})
            st.success("已保存")

# ================= 页面：商品管理 =================
elif page == "商品管理":
    st.markdown('<p class="main-header">商品管理</p>', unsafe_allow_html=True)
    products = load_products()
    with st.expander("从 Excel 导入商品", expanded=True):
        upload = st.file_uploader("选择商品列表 Excel", type=["xls", "xlsx"], key="pm_upload")
        merge_mode = st.checkbox("同名时更新单价", value=True, key="pm_merge")
        if st.button("执行导入", key="pm_do"):
            if upload:
                import io
                imp, upd, err = import_products_from_excel(io.BytesIO(upload.getvalue()), products, merge=merge_mode)
                st.success(f"导入 {imp} 条，更新 {upd} 条。") if not err else st.error(err)
            else:
                st.warning("请先选择文件")
    if products:
        st.dataframe(pd.DataFrame(products), use_container_width=True, hide_index=True)
    else:
        st.info("暂无商品，请从 Excel 导入或到【销售】→ 销货单 中维护。")

# ================= 页面：总览 =================
elif page == "📊 总览":
    st.markdown('<p class="main-header">📊 财务总览</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">资产、收支、应收应付一览</p>', unsafe_allow_html=True)

    # 账户余额
    st.subheader("🏦 账户余额")
    acc_balances = []
    total_asset = 0
    for acc in accounts:
        bal = calc_account_balance(acc["id"], transactions, accounts)
        acc_balances.append((acc["name"], bal))
        total_asset += bal

    cols = st.columns(min(len(acc_balances), 4))
    for i, (name, bal) in enumerate(acc_balances):
        with cols[i % 4]:
            st.metric(name, f"¥ {bal:,.2f}")

    st.metric("**资产合计**", f"¥ {total_asset:,.2f}")

    # 应收应付
    receivables, payables = calc_debt_summary(debt_records)
    rec_total = sum(receivables.values())
    pay_total = sum(payables.values())
    net_debt = rec_total - pay_total

    st.markdown("---")
    st.subheader("📥 往来账款")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("应收（别人欠我）", f"¥ {rec_total:,.2f}")
    with c2:
        st.metric("应付（我欠别人）", f"¥ {pay_total:,.2f}")
    with c3:
        st.metric("往来净额", f"¥ {net_debt:,.2f}")

    # 本月收支
    df = pd.DataFrame(transactions)
    if df.empty:
        inc, exp = 0, 0
    else:
        df["type"] = df["type"].fillna("")
        df = df[~df["type"].isin(["转账", "借出", "借入", "还入", "还出"])]
        if df.empty:
            inc, exp = 0, 0
        else:
            df["date"] = pd.to_datetime(df["date"])
            now = datetime.now()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            df_month = df[df["date"] >= month_start]
            inc = df_month[df_month["type"] == "收入"]["amount"].sum()
            exp = df_month[df_month["type"] == "支出"]["amount"].sum()

    st.markdown("---")
    st.subheader("📈 本月收支")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("本月收入", f"¥ {inc:,.2f}")
    with c2:
        st.metric("本月支出", f"¥ {exp:,.2f}")
    with c3:
        st.metric("本月结余", f"¥ {(inc - exp):,.2f}")

    # 图表
    if not df.empty:
        st.markdown("---")
        st.subheader("收支趋势")
        df["amount"] = df.apply(lambda r: r["amount"] if r["type"] == "收入" else -r["amount"], axis=1)
        daily = df.groupby(df["date"].dt.date)["amount"].sum().reset_index()
        daily.columns = ["日期", "金额"]
        daily["日期"] = pd.to_datetime(daily["日期"])
        import plotly.express as px
        fig = px.bar(daily, x="日期", y="金额", color="金额",
                     color_continuous_scale=["#eb3349", "#f45c43", "#38ef7d", "#11998e"])
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)


# ================= 页面：记一笔 =================
elif page == "➕ 记一笔":
    st.markdown('<p class="main-header">➕ 记一笔</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">记录收入或支出，选择入账账户</p>', unsafe_allow_html=True)

    with st.form("add_form"):
        col1, col2 = st.columns(2)
        with col1:
            t_type = st.radio("类型", ["收入", "支出"], horizontal=True)
            amount = st.number_input("金额 (元)", min_value=0.01, step=0.01, format="%.2f")
            cats = categories["income"] if t_type == "收入" else categories["expense"]
            category = st.selectbox("分类", cats)
            account = st.selectbox("入账账户", accounts, format_func=lambda x: x["name"])
        with col2:
            date = st.date_input("日期", value=datetime.now())
            note = st.text_input("备注", placeholder="如：午餐、工资等")

        if st.form_submit_button("保存"):
            add_transaction(transactions, t_type, amount, category, note, date, account_id=account["id"])
            st.success(f"已记录：{t_type} ¥{amount:,.2f} → {account['name']}")
            st.rerun()


# ================= 页面：转账 =================
elif page == "🔄 转账":
    st.markdown('<p class="main-header">🔄 账户转账</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">账户间资金划转</p>', unsafe_allow_html=True)

    with st.form("transfer_form"):
        col1, col2 = st.columns(2)
        with col1:
            from_acc = st.selectbox("转出账户", accounts, format_func=lambda x: x["name"])
            amount = st.number_input("金额 (元)", min_value=0.01, step=0.01, format="%.2f")
        with col2:
            to_acc = st.selectbox("转入账户", accounts, format_func=lambda x: x["name"])
            date = st.date_input("日期", value=datetime.now())
        note = st.text_input("备注", placeholder="如：提现、充值等")

        if st.form_submit_button("确认转账"):
            if from_acc["id"] == to_acc["id"]:
                st.error("转出和转入账户不能相同")
            else:
                add_transaction(transactions, "转账", amount, "", note, date,
                               from_account_id=from_acc["id"], to_account_id=to_acc["id"])
                st.success(f"已转账 ¥{amount:,.2f}：{from_acc['name']} → {to_acc['name']}")
                st.rerun()


# ================= 页面：流水记录 =================
elif page == "📋 流水记录":
    st.markdown('<p class="main-header">📋 流水记录</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">收支、转账、往来明细</p>', unsafe_allow_html=True)

    all_records = []
    acc_names = {a["id"]: a["name"] for a in accounts}

    for t in transactions:
        t_type = t.get("type", "")
        if t_type == "转账":
            from_n = acc_names.get(t.get("from_account_id"), "?")
            to_n = acc_names.get(t.get("to_account_id"), "?")
            desc = f"{from_n} → {to_n}"
        else:
            desc = t.get("category", "")
            acc_n = acc_names.get(t.get("account_id"), "")
            if acc_n:
                desc = f"{desc} ({acc_n})"
        all_records.append({
            "日期": t["date"],
            "类型": t_type,
            "说明": desc,
            "金额": t["amount"],
            "备注": t.get("note", "")
        })

    for d in debt_records:
        acc_n = acc_names.get(d.get("account_id"), "")
        all_records.append({
            "日期": d["date"],
            "类型": d["type"],
            "说明": f"{d.get('contact','')} {acc_n}".strip(),
            "金额": d["amount"],
            "备注": d.get("note", "")
        })

    if not all_records:
        st.info("暂无流水记录。")
    else:
        df = pd.DataFrame(all_records)
        df = df.sort_values("日期", ascending=False)

        col1, col2 = st.columns(2)
        with col1:
            f_type = st.selectbox("类型", ["全部", "收入", "支出", "转账", "借出", "借入", "还入", "还出"])
        with col2:
            f_month = st.text_input("月份 (如 2025-02)", placeholder="留空显示全部")

        if f_type != "全部":
            df = df[df["类型"] == f_type]
        if f_month.strip():
            df = df[df["日期"].str.startswith(f_month.strip())]

        df_display = df.copy()
        df_display["金额"] = df_display.apply(
            lambda r: f"+{r['金额']:,.2f}" if r["类型"] in ("收入", "借入", "还入") else f"-{r['金额']:,.2f}",
            axis=1
        )
        st.dataframe(df_display, use_container_width=True, hide_index=True)


# ================= 页面：应收应付 =================
elif page == "📥 应收应付":
    st.markdown('<p class="main-header">📥 应收应付</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">借出、借入、还入、还出管理</p>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["记一笔", "往来明细", "往来汇总"])

    with tab1:
        with st.form("debt_form"):
            d_type = st.radio("类型", ["借出", "借入", "还入", "还出"], horizontal=True)
            contact = st.text_input("对方（姓名/单位）", placeholder="如：张三、XX公司")
            amount = st.number_input("金额 (元)", min_value=0.01, step=0.01, format="%.2f")
            account = st.selectbox("关联账户", accounts, format_func=lambda x: x["name"])
            date = st.date_input("日期", value=datetime.now())
            note = st.text_input("备注")

            if st.form_submit_button("保存"):
                add_debt_record(debt_records, d_type, contact, amount, account["id"], date, note)
                add_transaction(transactions, d_type, amount, "", note, date, account_id=account["id"])
                st.success(f"已记录：{d_type} ¥{amount:,.2f} - {contact}")
                st.rerun()

    with tab2:
        if not debt_records:
            st.info("暂无往来记录。")
        else:
            df = pd.DataFrame(debt_records)
            df = df.sort_values("date", ascending=False)
            acc_map = {a["id"]: a["name"] for a in accounts}
            df["账户"] = df["account_id"].map(acc_map)
            st.dataframe(df[["date", "type", "contact", "amount", "账户", "note"]], use_container_width=True, hide_index=True)

    with tab3:
        rec, pay = calc_debt_summary(debt_records)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("应收（别人欠我）")
            if rec:
                for p, amt in sorted(rec.items(), key=lambda x: -x[1]):
                    st.write(f"**{p}**: ¥{amt:,.2f}")
            else:
                st.info("无应收")
        with col2:
            st.subheader("应付（我欠别人）")
            if pay:
                for p, amt in sorted(pay.items(), key=lambda x: -x[1]):
                    st.write(f"**{p}**: ¥{amt:,.2f}")
            else:
                st.info("无应付")


# ================= 页面：预算管理 =================
elif page == "📈 预算管理":
    st.markdown('<p class="main-header">📈 预算管理</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">设置月度预算，控制支出</p>', unsafe_allow_html=True)

    now = datetime.now()
    month_key = now.strftime("%Y-%m")
    if month_key not in budgets:
        budgets[month_key] = {}

    st.subheader(f"本月预算 ({month_key})")
    for cat in categories["expense"]:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(f"**{cat}**")
        with col2:
            val = budgets[month_key].get(cat, 0)
            new_val = st.number_input(f"预算", key=f"b_{cat}", value=float(val) if val else 0.0,
                                     min_value=0.0, step=100.0, format="%.0f", label_visibility="collapsed")
            if new_val != val:
                budgets[month_key][cat] = new_val
                save_json(BUDGETS_FILE, budgets)

    st.markdown("---")
    st.subheader("预算执行")
    df = pd.DataFrame(transactions)
    if df.empty or "type" not in df.columns:
        df = pd.DataFrame()
    else:
        df = df[(df["type"] == "支出")]
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df_month = df[df["date"].dt.strftime("%Y-%m") == month_key]
        if not df_month.empty:
            exp_by_cat = df_month.groupby("category")["amount"].sum()
            for cat in categories["expense"]:
                spent = exp_by_cat.get(cat, 0)
                budget = budgets[month_key].get(cat, 0)
                if budget > 0:
                    pct = min(1.0, spent / budget)
                    st.write(f"**{cat}**: ¥{spent:,.0f} / ¥{budget:,.0f} ({pct*100:.0f}%)")
                    st.progress(pct)
        else:
            st.info("本月暂无支出。")
    else:
        st.info("暂无支出记录。")


# ================= 页面：账户管理 =================
elif page == "🏦 账户管理":
    st.markdown('<p class="main-header">🏦 账户管理</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">管理银行卡、现金、支付宝、微信等账户</p>', unsafe_allow_html=True)

    st.subheader("账户列表")
    for acc in accounts:
        bal = calc_account_balance(acc["id"], transactions, accounts)
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.write(f"**{acc['name']}** ({acc.get('type','')})")
        with col2:
            st.write(f"当前余额: ¥{bal:,.2f}")
        with col3:
            if st.button("删除", key=f"del_{acc['id']}"):
                accounts.remove(acc)
                save_accounts(accounts)
                st.rerun()

    st.markdown("---")
    st.subheader("添加账户")
    with st.form("add_acc"):
        name = st.text_input("账户名称", placeholder="如：工商银行")
        acc_type = st.selectbox("类型", ["现金", "银行卡", "支付宝", "微信", "其他"])
        init = st.number_input("期初余额", value=0.0, step=100.0, format="%.2f")
        if st.form_submit_button("添加"):
            accounts.append({
                "id": next_id(accounts),
                "name": name or "新账户",
                "type": acc_type,
                "init_balance": init
            })
            save_accounts(accounts)
            st.success("已添加")
            st.rerun()

    st.markdown("---")
    st.subheader("调整期初余额")
    with st.form("init_balance"):
        acc = st.selectbox("账户", accounts, format_func=lambda x: x["name"])
        new_init = st.number_input("新期初余额", value=float(acc.get("init_balance", 0)), step=100.0, format="%.2f")
        if st.form_submit_button("保存"):
            acc["init_balance"] = new_init
            save_accounts(accounts)
            st.success("已更新")
            st.rerun()


# ================= 页面：销售出库单 =================
elif page == "📄 销售出库单":
    st.markdown('<p class="main-header">📄 销售出库单</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">开单、保存、打印预览（下载 HTML 后浏览器打开即可打印）</p>', unsafe_allow_html=True)

    delivery_notes = load_delivery_notes()
    company = load_company()

    with st.expander("公司信息（用于单据说头与表尾）", expanded=False):
        c_name = st.text_input("公司名称", value=company.get("name", ""), key="co_name")
        c_title = st.text_input("单据说头", value=company.get("title", "销售出库单"), key="co_title")
        c_scope = st.text_input("主营", value=company.get("business_scope", ""), key="co_scope")
        c_phones = st.text_input("联系电话", value=company.get("contact_phones", ""), key="co_phones")
        c_handler = st.text_input("默认经手人", value=company.get("default_handler", ""), key="co_handler")
        c_preparer = st.text_input("默认制单人", value=company.get("default_preparer", ""), key="co_preparer")
        if st.button("保存公司信息"):
            save_company({
                "name": c_name, "title": c_title, "business_scope": c_scope, "contact_phones": c_phones,
                "default_handler": c_handler, "default_preparer": c_preparer,
            })
            st.success("已保存")

    # 商品库 / 从 Excel 导入
    products = load_products()
    with st.expander("商品库 / 从 Excel 导入商品清单", expanded=True):
        st.caption("支持 .xls、.xlsx，自动识别「商品名称/名称/品名」和「单价/价格/零售价」等列。")
        upload = st.file_uploader("选择商品列表 Excel", type=["xls", "xlsx"], key="product_upload")
        path_input = st.text_input("或填写本地文件路径", placeholder=r"例如: C:\Users\Administrator\Desktop\商品列表.xls", key="product_path")
        col_imp, col_merge, _ = st.columns([1, 1, 2])
        with col_imp:
            do_import = st.button("执行导入", key="do_import")
        with col_merge:
            merge_mode = st.checkbox("同名时更新单价", value=True, key="merge_price")
        if do_import:
            if upload is not None:
                import io
                imported, updated, err = import_products_from_excel(io.BytesIO(upload.getvalue()), products, merge=merge_mode)
            elif path_input and path_input.strip():
                from pathlib import Path
                p = Path(path_input.strip().strip('"'))
                if not p.exists():
                    st.error(f"文件不存在: {p}")
                else:
                    imported, updated, err = import_products_from_excel(str(p), products, merge=merge_mode)
            else:
                err = "请先选择上传文件或填写本地路径"
                imported, updated = 0, 0
            if err:
                st.error(err)
            else:
                st.success(f"成功导入 {imported} 条，更新 {updated} 条。商品库共 {len(products)} 条。")
        if products:
            st.caption("从商品库添加一行到下方明细：")
            sel = st.selectbox("选择商品", options=[p.get("name", "") for p in products], key="sel_product")
            if st.button("添加一行到明细", key="add_product_row"):
                pr = next((p for p in products if p.get("name") == sel), None)
                price = float(pr.get("unit_price", 0)) if pr else 0
                new_row = pd.DataFrame([{"商品名称": sel, "数量": 1.0, "单价": price, "备注": ""}])
                st.session_state.out_lines = pd.concat([st.session_state.out_lines, new_row], ignore_index=True)
                st.rerun()

    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    same_day = [n for n in delivery_notes if (n.get("record_date") or "").startswith(now.strftime("%Y-%m-%d"))]
    next_seq = len(same_day) + 1
    default_number = f"XS-{now.strftime('%Y%m%d')}-{next_seq:03d}"

    if "out_lines" not in st.session_state:
        st.session_state.out_lines = pd.DataFrame({
            "商品名称": ["", "", ""],
            "数量": [0.0, 0.0, 0.0],
            "单价": [0.0, 0.0, 0.0],
            "备注": ["", "", ""],
        })

    st.subheader("填写出库单")
    col1, col2, col3 = st.columns(3)
    with col1:
        record_date = st.text_input("录单日期", value=today_str, key="rec_date")
        handler = st.text_input("经手人", value=company.get("default_handler", ""), key="handler")
        number = st.text_input("编号", value=default_number, key="number")
    with col2:
        summary = st.text_input("摘要", value="", key="summary")
        buyer = st.text_input("购买单位", value="", key="buyer")
        buyer_phone = st.text_input("联系电话", value="", key="buyer_phone")
    with col3:
        preparer = st.text_input("制单人", value=company.get("default_preparer", ""), key="preparer")
        discount = st.number_input("优惠金额", value=0.0, min_value=0.0, step=0.01, format="%.2f", key="discount")

    edited = st.data_editor(
        st.session_state.out_lines,
        column_config={
            "商品名称": st.column_config.TextColumn("商品名称", width="large"),
            "数量": st.column_config.NumberColumn("数量", min_value=0.0, step=0.1, format="%.2f"),
            "单价": st.column_config.NumberColumn("单价", min_value=0.0, step=0.01, format="%.2f"),
            "备注": st.column_config.TextColumn("备注", width="medium"),
        },
        num_rows="dynamic",
        key="lines_editor",
    )
    st.session_state.out_lines = edited

    # 计算金额与合计
    edited["金额"] = (edited["数量"].fillna(0) * edited["单价"].fillna(0)).round(2)
    subtotal = float(edited["金额"].sum())
    total = subtotal - float(discount)
    st.caption(f"明细小计: ¥{subtotal:.2f}  －  优惠: ¥{float(discount):.2f}  ＝  合计: ¥{total:.2f}")

    col_save, col_print, _ = st.columns([1, 1, 2])
    with col_save:
        if st.button("保存出库单"):
            # 1) 旧版结构：仍然写入 delivery_notes.json，保持兼容
            lines_raw = edited.drop(columns=["金额"], errors="ignore")
            lines_raw = lines_raw[lines_raw["商品名称"].astype(str).str.strip() != ""]
            lines_list = []
            for _, row in lines_raw.iterrows():
                lines_list.append({
                    "product_name": str(row.get("商品名称", "")),
                    "quantity": float(row.get("数量", 0) or 0),
                    "unit_price": float(row.get("单价", 0) or 0),
                    "amount": float(row.get("数量", 0) or 0) * float(row.get("单价", 0) or 0),
                    "remark": str(row.get("备注", "")),
                })
            note = {
                "id": next_id(delivery_notes),
                "number": number,
                "record_date": record_date,
                "handler": handler,
                "summary": summary,
                "buyer": buyer,
                "buyer_phone": buyer_phone,
                "lines": lines_list,
                "discount": float(discount),
                "total": total,
                "preparer": preparer,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            delivery_notes.append(note)
            save_delivery_notes(delivery_notes)

            # 2) 新版结构：写入 sales_header / sales_detail / stock_moves / arap_moves
            sales_headers = load_json(SALES_HEADER_FILE, [])
            sales_details = load_json(SALES_DETAIL_FILE, [])
            stock_moves = load_json(STOCK_MOVES_FILE, [])
            arap_moves = load_json(ARAP_MOVES_FILE, [])

            header_id = f"XS{record_date.replace('-', '')}-{len(sales_headers)+1:03d}"
            customer_id = buyer or "C_TMP"  # 先用名称占位，后续可改为真实客户档案

            header = {
                "id": header_id,
                "no": number,
                "biz_date": record_date,
                "customer_id": customer_id,
                "warehouse_id": "W01",
                "settle_account_id": None,
                "amount_total": subtotal,
                "discount_total": float(discount),
                "amount_payable": total,
                "amount_received": 0.0,
                "amount_ar": total,
                "status": "checked",
                "salesman": handler,
                "handler": handler,
                "summary": summary,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            sales_headers.append(header)

            # 明细与库存流水
            line_idx = 1
            for l in lines_list:
                detail_id = f"{header_id}-{line_idx:02d}"
                line_idx += 1
                qty = float(l["quantity"])
                price = float(l["unit_price"])
                amount = float(l["amount"])
                goods_id = l["product_name"]  # 先用名称占位，后续可切换为真正 goods_id

                sales_details.append({
                    "id": detail_id,
                    "header_id": header_id,
                    "goods_id": goods_id,
                    "warehouse_id": "W01",
                    "qty": qty,
                    "unit": "",
                    "price": price,
                    "discount_rate": 0.0,
                    "tax_rate": 0.0,
                    "amount": amount,
                    "note": l.get("remark", ""),
                })

                stock_moves.append({
                    "id": detail_id,
                    "biz_date": record_date,
                    "bill_type": "sale",
                    "bill_no": number,
                    "goods_id": goods_id,
                    "warehouse_id": "W01",
                    "qty_in": 0.0,
                    "qty_out": qty,
                    "cost_price": price,  # 先用售价占位，后续可用真实成本
                    "amount_cost": qty * price,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })

            # 往来流水：客户应收
            arap_moves.append({
                "id": header_id,
                "biz_date": record_date,
                "obj_type": "customer",
                "obj_id": customer_id,
                "bill_type": "sale",
                "bill_no": number,
                "debit": total,
                "credit": 0.0,
                "note": summary,
            })

            save_json(SALES_HEADER_FILE, sales_headers)
            save_json(SALES_DETAIL_FILE, sales_details)
            save_json(STOCK_MOVES_FILE, stock_moves)
            save_json(ARAP_MOVES_FILE, arap_moves)

            st.success("已保存出库单，并写入销货单/库存/应收结构")

    with col_print:
        lines_for_html = []
        for _, row in edited.iterrows():
            if str(row.get("商品名称", "") or "").strip():
                q, p = row.get("数量", 0), row.get("单价", 0)
                if pd.isna(q):
                    q = 0
                if pd.isna(p):
                    p = 0
                lines_for_html.append({
                    "product_name": row.get("商品名称"),
                    "quantity": q,
                    "unit_price": p,
                    "remark": row.get("备注", "") or "",
                })
        html_content = build_receipt_html(
            company, record_date, handler, number, summary, buyer, buyer_phone,
            lines_for_html, discount, total, preparer,
        )
        st.download_button(
            "打印预览（下载 HTML）",
            data=html_content,
            file_name=f"出库单_{number}.html",
            mime="text/html",
            key="dl_receipt",
        )
    st.caption("下载后双击 HTML 文件用浏览器打开，按 Ctrl+P 打印或另存为 PDF。")

    if delivery_notes:
        st.markdown("---")
        st.subheader("已保存的出库单")
        for n in reversed(delivery_notes[-20:]):
            st.text(f"{n.get('record_date','')}  {n.get('number','')}  {n.get('buyer','')}  合计 ¥{n.get('total',0):.2f}")


# ================= 页面：客户账单 =================
elif page == "👤 客户账单":
    st.markdown('<p class="main-header">👤 客户账单</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">按客户查看：何时买了多少货、已付多少、还欠多少</p>', unsafe_allow_html=True)

    delivery_notes = load_delivery_notes()
    payments = load_payments()

    # 客户列表：出库单里出现过的购买单位
    customers = sorted(set(str(n.get("buyer", "") or "").strip() for n in delivery_notes if str(n.get("buyer", "") or "").strip()))
    if not customers:
        st.info("暂无客户数据，请先在「销售出库单」中开单并填写购买单位。")
    else:
        customer = st.selectbox("选择客户", options=customers, key="bill_customer")
        if customer:
            # 该客户的出库单
            notes_for_customer = [n for n in delivery_notes if (str(n.get("buyer", "") or "").strip() == customer)]
            notes_for_customer.sort(key=lambda x: x.get("record_date", "") or "", reverse=True)

            # 该客户的收款记录
            pays_for_customer = [p for p in payments if (str(p.get("customer", "") or "").strip() == customer)]
            pays_for_customer.sort(key=lambda x: x.get("date", "") or "", reverse=True)

            # 汇总
            sales_total = sum(float(n.get("total", 0) or 0) for n in notes_for_customer)
            paid_total = sum(float(p.get("amount", 0) or 0) for p in pays_for_customer)
            balance = sales_total - paid_total

            st.subheader("汇总")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("出库合计", f"¥ {sales_total:,.2f}")
            with col2:
                st.metric("已付合计", f"¥ {paid_total:,.2f}")
            with col3:
                st.metric("还欠", f"¥ {balance:,.2f}")

            st.markdown("---")
            st.subheader("出库明细（什么时候买了多少货）")
            if notes_for_customer:
                df_notes = pd.DataFrame([
                    {
                        "日期": n.get("record_date", ""),
                        "单号": n.get("number", ""),
                        "合计金额": float(n.get("total", 0) or 0),
                        "备注": n.get("summary", ""),
                    }
                    for n in notes_for_customer
                ])
                st.dataframe(df_notes, use_container_width=True, hide_index=True)
            else:
                st.caption("该客户暂无出库单。")

            st.markdown("---")
            st.subheader("收款记录（已付多少钱）")
            if pays_for_customer:
                df_pays = pd.DataFrame([
                    {
                        "日期": p.get("date", ""),
                        "金额": float(p.get("amount", 0) or 0),
                        "备注": p.get("note", ""),
                    }
                    for p in pays_for_customer
                ])
                st.dataframe(df_pays, use_container_width=True, hide_index=True)
            else:
                st.caption("该客户暂无收款记录。")

            # 登记收款
            with st.expander("登记该客户收款"):
                with st.form("add_payment"):
                    pay_date = st.date_input("收款日期", value=datetime.now(), key="pay_date")
                    pay_amount = st.number_input("收款金额", min_value=0.01, step=0.01, format="%.2f", key="pay_amount")
                    pay_note = st.text_input("备注", placeholder="如：银行转账、现金", key="pay_note")
                    if st.form_submit_button("保存收款"):
                        payments.append({
                            "id": next_id(payments),
                            "customer": customer,
                            "amount": float(pay_amount),
                            "date": pay_date.strftime("%Y-%m-%d"),
                            "note": pay_note or "",
                            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        })
                        save_payments(payments)
                        st.success("已登记收款")
                        st.rerun()


# ================= 页面：分类设置 =================
elif page == "⚙️ 分类设置":
    st.markdown('<p class="main-header">⚙️ 分类设置</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">自定义收支分类</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("收入分类")
        inc = st.text_area("每行一个", value="\n".join(categories["income"]), height=150)
        if st.button("保存收入分类"):
            categories["income"] = [x.strip() for x in inc.split("\n") if x.strip()]
            save_categories(categories)
            st.success("已保存")
    with col2:
        st.subheader("支出分类")
        exp = st.text_area("每行一个", value="\n".join(categories["expense"]), height=150, key="exp")
        if st.button("保存支出分类"):
            categories["expense"] = [x.strip() for x in exp.split("\n") if x.strip()]
            save_categories(categories)
            st.success("已保存")
