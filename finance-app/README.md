# 国宇制冷理财管家（云部署版）

多账户、应收应付、转账、销售出库单、客户账单等。本地/便携包数据在 `data/`；云上部署时数据在应用目录下 `data/`（Streamlit Cloud 为临时存储，重启可能清空，仅适合演示或短期使用）。

## 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 部署到 Streamlit Community Cloud

见仓库根目录 **`部署说明-理财软件上云.md`**。
