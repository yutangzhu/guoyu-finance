# 国宇理财 · 迷你云式进销存数据结构草案

> 说明：本结构既适合 JSON 文件存储，也方便以后迁移到数据库。

## 1. 基础档案（Master Data）

- `goods` 商品档案  
  字段：`id, name, spec, unit, barcode, category, purchase_price, sale_price, tax_rate, enabled, created_at`

- `customers` 客户档案  
  字段：`id, name, contact, phone, address, level, settle_type, credit_limit, note`

- `suppliers` 供应商档案  
  字段：`id, name, contact, phone, address, settle_type, note`

- `warehouses` 仓库档案  
  字段：`id, name, address, manager, enabled`

- `accounts` 资金账户（已存在）  
  字段：`id, name, type, init_balance, enabled`

## 2. 单据：销货单（销售出库）

- `sales_header` 销货单主表  
  字段（建议）：  
  - `id` 内部主键  
  - `no` 单号（如 `XS-20250226-001`）  
  - `biz_date` 单据日期  
  - `customer_id` 客户  
  - `warehouse_id` 仓库  
  - `settle_account_id` 收款账户（可空）  
  - `amount_total` 商品金额合计  
  - `discount_total` 整单优惠  
  - `amount_payable` 应收金额  
  - `amount_received` 本次收款  
  - `amount_ar` 本单形成应收  
  - `status` 单据状态（`draft / checked / void`）  
  - `salesman, handler, summary, created_at`

- `sales_detail` 销货单明细  
  字段：`id, header_id, goods_id, warehouse_id, qty, unit, price, discount_rate, tax_rate, amount, note`

## 3. 库存流水

- `stock_moves` 库存变动记录  
  字段：`id, biz_date, bill_type, bill_no, goods_id, warehouse_id, qty_in, qty_out, cost_price, amount_cost, created_at`

## 4. 往来流水（应收应付）

- `arap_moves` 往来账户收付流水  
  字段：`id, biz_date, obj_type(customer/supplier), obj_id, bill_type(sale/receipt/purchase/payment/adjust), bill_no, debit, credit, note`

> 当前实现优先在保存“销售出库单”时写入 `sales_header`、`sales_detail`、`stock_moves`、`arap_moves` 四类 JSON 文件，其它单据可后续按此结构扩展。

