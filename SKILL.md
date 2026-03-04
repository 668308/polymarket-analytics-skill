---
name: polymarket-analytics
description: Polymarket 预测市场分析工具。提供钱包分析、模拟回测、市场分析、策略建议、自我进化五大功能。支持自动学习聪明钱模式、实时进化交易原则、持续提高准确度，但不涉及真实交易。

user-invocable: true
metadata:
  openclaw:
    emoji: ":crystal_ball:"
    bins:
      - python3
      - pip3
    install:
      - id: python3
        kind: apt
        package: python3
      - id: pip3
        kind: apt
        package: python3-pip
    os:
      - linux
      - darwin
  version: "1.1.0"
  author: "虾米"
  keywords:
    - polymarket
    - 预测市场
    - 钱包分析
    - 回测
    - 策略
    - 自动进化
    - 机器学习
---

# Polymarket Analytics Skill

Polymarket 预测市场分析工具，集成自动学习系统，能够：
- ✅ 分析聪明钱钱包特征
- ✅ 自动学习交易模式
- ✅ 进化交易原则库
- ✅ 持续提高准确度

**⚠️ 重要说明**: 本工具仅用于分析，不执行真实交易，不接触私钥。

## 🆕 自动进化系统 (Auto-Evolution)

### 核心特性

| 特性 | 说明 |
|------|------|
| **自动学习** | 扫描钱包时自动提取交易模式 |
| **原则生成** | 基于成功模式自动生成交易原则 |
| **信号验证** | 追踪原则准确度并反馈优化 |
| **持续进化** | 定期淘汰低效原则，生成优化变体 |
| **智能建议** | 基于进化后的原则生成实时建议 |

### 交易原则库

系统自动维护一个交易原则库，每个原则包含：
- **条件**: 触发原则的市场/钱包特征
- **操作**: 建议的交易行为
- **准确度**: 历史验证成功率
- **信心度**: 系统对原则的置信度

原则会自动进化：
- 🟢 高准确度原则 → 信心度提升
- 🟡 中等准确度 → 保留观察
- 🔴 低准确度原则 → 淘汰删除

## API 基础信息

| API | URL | 用途 |
|-----|-----|------|
| **Gamma API** | `https://gamma-api.polymarket.com` | 市场、事件、搜索 |
| **Data API** | `https://data-api.polymarket.com` | 用户持仓、交易数据 |
| **CLOB API** | `https://clob.polymarket.com` | 订单簿、价格历史 |

## 七大核心功能

### 1. 智能钱包扫描 (Smart Scan)

**自动学习版钱包分析** - 扫描时自动生成交易原则。

```bash
python3 scripts/smart_scanner.py -w 0x56687bf447db6ffa42ffe2204a05edaa20f55839
```

**功能**:
- 分析钱包表现
- 自动学习交易模式
- 生成交易原则
- 提供智能建议

### 2. 自动进化系统 (Auto-Evolution)

**核心进化引擎** - 独立运行的学习和进化模块。

```bash
# 分析钱包并学习
python3 scripts/auto_evolution.py -w 0x...

# 验证历史信号
python3 scripts/auto_evolution.py -v

# 进化原则库
python3 scripts/auto_evolution.py -e

# 查看最佳原则
python3 scripts/auto_evolution.py -b
```

**进化流程**:
1. 扫描钱包 → 提取模式特征
2. 生成原则 → 加入原则库
3. 检测信号 → 记录预测结果
4. 验证结果 → 更新准确度
5. 触发进化 → 淘汰/优化原则

### 3. 钱包分析 (Wallet Analysis)

基础版钱包分析（不启用自动学习）。

```bash
python3 scripts/wallet_analysis.py --address 0x...
```

**输出指标**:
- 胜率 (Win Rate)
- 盈亏比 (PnL)
- 夏普比率 (Sharpe Ratio)
- 最大回撤 (Max Drawdown)

### 4. 模拟回测 (Backtesting)

模拟跟随指定钱包的历史表现。

```bash
python3 scripts/backtesting.py \
  --target 0x... \
  --days 90 \
  --investment 1000
```

### 5. 市场分析 (Market Analysis)

获取 Polymarket 热门市场数据。

```bash
python3 scripts/market_analysis.py
```

### 6. 策略建议 (Strategy Suggestions)

基于数据生成交易建议。

```bash
python3 scripts/strategy_suggestions.py --risk-level moderate
```

### 7. 批量/持续监控

**批量扫描**:
```bash
python3 scripts/smart_scanner.py -b 0xaddr1 0xaddr2 0xaddr3
```

**持续监控模式**:
```bash
python3 scripts/smart_scanner.py -m 0xaddr1 0xaddr2 --interval 30
```

## 数据文件

| 文件 | 说明 |
|------|------|
| `data/wallet_cache.json` | 钱包数据缓存 |
| `data/market_cache.json` | 市场数据缓存 |
| `data/strategies.json` | 策略参数存储 |
| `data/trading_principles.json` | 交易原则库 |
| `data/signal_history.json` | 信号历史记录 |
| `data/learning_log.jsonl` | 学习日志 |
| `data/scan_history.json` | 扫描历史 |

## 使用示例

### 快速开始 - 智能扫描

```bash
# 1. 扫描一个钱包并自动学习
python3 scripts/smart_scanner.py -w 0x56687bf447db6ffa42ffe2204a05edaa20f55839

# 2. 查看生成的原则
python3 scripts/auto_evolution.py -l

# 3. 查看最佳原则
python3 scripts/auto_evolution.py -b
```

### 批量发现聪明钱

```bash
# 准备钱包地址列表
WALLETS="0xaddr1 0xaddr2 0xaddr3 0xaddr4 0xaddr5"

# 批量扫描（会自动学习并进化）
python3 scripts/smart_scanner.py -b $WALLETS

# 系统会：
# - 分析每个钱包
# - 生成交易原则
# - 识别聪明钱
# - 触发原则进化
```

### 持续监控聪明钱

```bash
# 监控多个聪明钱钱包，每30分钟检查一次
python3 scripts/smart_scanner.py \
  -m 0xsmart1 0xsmart2 0xsmart3 \
  --interval 30
```

## 自动进化工作原理

### 1. 模式识别

```python
# 从钱包交易历史中提取特征
{
  "win_rate": 65.5,           # 胜率
  "avg_hold_time": 48.5,      # 平均持仓时间(小时)
  "avg_position_size": 500,   # 平均仓位
  "profit_factor": 1.8        # 盈亏比
}
```

### 2. 原则生成

基于模式自动生成原则：

```python
{
  "id": "p_wallet123_win",
  "name": "高胜率钱包跟随策略",
  "condition": "wallet.win_rate > 60",
  "action": "跟随买入，仓位5%，止盈30%止损15%",
  "confidence": 70.0,
  "accuracy": 0.0  # 等待验证
}
```

### 3. 信号验证

系统会追踪每个原则产生的信号：

```python
{
  "signal_id": "sig_123",
  "principle_id": "p_wallet123_win",
  "direction": "buy",
  "outcome": "success",  # 或 "fail"
  "validated": true
}
```

### 4. 原则进化

根据验证结果调整原则：

```python
# 准确度 > 70% → 信心度提升
if accuracy > 70:
    confidence = min(95, confidence + 2)

# 准确度 < 40% → 信心度降低，最终淘汰
if accuracy < 40:
    confidence = max(30, confidence - 5)
```

## 准确度提升路径

```
第1轮扫描 → 生成初始原则 (准确度未知)
    ↓
第2轮验证 → 验证信号结果 (收集数据)
    ↓
第3轮进化 → 淘汰低效原则 (筛选)
    ↓
第4轮优化 → 生成优化变体 (迭代)
    ↓
持续循环 → 原则库逐渐精准
```

## 免责声明

⚠️ **风险提示**:
- 本工具仅提供数据分析，不构成投资建议
- 预测市场交易存在高风险，可能损失全部本金
- 历史表现不代表未来收益
- 自动进化系统需要足够数据才能达到稳定准确度
- 请根据自身风险承受能力谨慎决策

## 技术说明

**依赖库**:
- requests (HTTP 请求)
- numpy (数值计算)
- dataclasses (数据结构)

**进化算法**:
- 基于规则的遗传算法
- 优胜劣汰选择机制
- 参数微调优化
- 多代迭代进化

**数据来源**:
- Polymarket 官方 API
- 数据更新频率: 实时
- 原则库更新: 每5个钱包或手动触发

## 更新日志

- **v1.1.0** (2026-03-04): 新增自动进化系统
  - 自动学习钱包模式
  - 交易原则库管理
  - 信号验证与反馈
  - 智能扫描集成

- **v1.0.0** (2026-03-04): 初始版本
  - 钱包分析
  - 模拟回测
  - 市场分析
  - 策略建议
  - 基础自我进化
