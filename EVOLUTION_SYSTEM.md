# Polymarket Analytics Skill - 完整自动进化系统

## 🧬 系统概述

本系统实现了 **5大核心模块的完全自动进化**，让每个模块都能：
- ✅ 自我学习优化
- ✅ 自动调整参数
- ✅ 生成新的策略规则
- ✅ 持续提升准确度

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│              中央进化引擎 (Central Evolution Engine)        │
│                   - 协调所有模块进化                        │
│                   - 管理进化规则库                         │
│                   - 记录性能数据                           │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ 钱包分析模块  │   │ 模拟回测模块  │   │ 市场分析模块  │
│ (进化适配器)  │   │ (进化适配器)  │   │ (进化适配器)  │
└──────────────┘   └──────────────┘   └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
                   ┌──────────────┐
                   │ 策略建议模块  │
                   │ (进化适配器)  │
                   └──────────────┘
                            │
                            ▼
                   ┌──────────────┐
                   │ 原则进化模块  │
                   │ (元进化)      │
                   └──────────────┘
```

## 📦 核心组件

### 1. 中央进化引擎 (`central_evolution_engine.py`)

**功能**:
- 协调5大模块的进化
- 维护进化规则库
- 记录性能指标
- 生成进化报告

**使用**:
```bash
python3 scripts/central_evolution_engine.py --run
```

### 2. 进化管理器 (`evolution_manager.py`)

**功能**:
- 自动调度进化任务
- 监控模块执行次数
- 触发适时进化
- 支持手动强制进化

**使用**:
```bash
# 启动自动进化系统
python3 scripts/evolution_manager.py --run

# 立即运行完整进化
python3 scripts/evolution_manager.py --evolve-now

# 强制进化特定模块
python3 scripts/evolution_manager.py --force wallet_analysis

# 查看进化状态
python3 scripts/evolution_manager.py --status

# 调整进化频率
python3 scripts/evolution_manager.py --adjust wallet_analysis 5
```

### 3. 进化版钱包分析 (`wallet_analysis_evolvable.py`)

**进化特性**:
- 自动识别最有效的分析指标
- 动态调整权重分配
- 学习历史成功案例
- 生成个性化推荐

**使用**:
```bash
# 分析钱包（自动进化）
python3 scripts/wallet_analysis_evolvable.py \
  --address 0x... \
  --days 90

# 查看学习洞察
python3 scripts/wallet_analysis_evolvable.py --insights
```

**进化触发**: 每分析10个钱包自动进化一次

### 4. 进化版回测 (`backtesting_evolvable.py`)

**进化特性**:
- 动态优化跟单比例
- 学习最优止盈止损点
- 改进仓位管理策略
- 生成策略变体

**使用**:
```bash
# 运行进化版回测
python3 scripts/backtesting_evolvable.py \
  --target 0x... \
  --days 90 \
  --strategy moderate

# 比较所有策略
python3 scripts/backtesting_evolvable.py \
  --target 0x... \
  --compare

# 查看性能洞察
python3 scripts/backtesting_evolvable.py --insights
```

**进化触发**: 每运行5次回测自动进化一次

## 🔄 进化流程

### 自动进化流程

```
1. 模块执行
   ↓
2. 记录性能数据 (成功率、执行时间、准确度)
   ↓
3. 检查是否达到进化阈值
   ↓
4. 触发进化 → 分析历史数据
   ↓
5. 识别成功模式
   ↓
6. 生成新的优化规则
   ↓
7. 更新模块配置
   ↓
8. 应用新的参数和策略
```

### 进化频率配置

| 模块 | 默认进化频率 | 可调范围 |
|------|-------------|----------|
| 钱包分析 | 每10次执行 | 5-20 |
| 模拟回测 | 每5次执行 | 3-10 |
| 市场分析 | 每3次执行 | 2-5 |
| 策略建议 | 每7次执行 | 5-15 |
| 原则进化 | 每15次执行 | 10-30 |

## 📊 进化效果追踪

### 性能数据文件

所有进化数据保存在 `data/` 目录：

```
data/
├── module_performance.json      # 模块性能统计
├── evolution_log.jsonl         # 进化日志
├── evolution_rules.json        # 进化规则库
├── wallet_analysis_evolved.json    # 钱包分析进化配置
├── backtesting_evolved.json        # 回测进化配置
├── market_analysis_evolved.json    # 市场分析进化配置
├── strategy_suggestions_evolved.json   # 策略建议进化配置
└── meta_evolution.json         # 元进化配置
```

### 进化报告

每次完整进化后生成报告：
```bash
data/evolution_report_YYYYMMDD_HHMMSS.json
```

报告内容包括：
- 各模块进化结果
- 新规则数量
- 性能改进数据
- 最优参数配置

## 🎯 使用示例

### 示例 1：完整的自动分析流程

```bash
# 1. 分析多个钱包（自动触发进化）
for addr in addr1 addr2 addr3 ...; do
    python3 scripts/wallet_analysis_evolvable.py -a $addr
done

# 2. 对最佳钱包进行回测（自动触发进化）
python3 scripts/backtesting_evolvable.py \
  --target 0xbest... \
  --strategy moderate

# 3. 查看系统进化状态
python3 scripts/evolution_manager.py --status

# 4. 手动触发完整进化
python3 scripts/evolution_manager.py --evolve-now
```

### 示例 2：比较不同策略

```bash
# 对比保守、稳健、激进三种策略
python3 scripts/backtesting_evolvable.py \
  --target 0x... \
  --compare

# 输出示例:
# {
#   "comparison": {
#     "conservative": {"return": 15.2, "sharpe": 1.8, "rating": "A"},
#     "moderate": {"return": 28.5, "sharpe": 2.1, "rating": "A+"},
#     "aggressive": {"return": 42.3, "sharpe": 1.5, "rating": "B+"}
#   },
#   "best_strategy": "moderate",
#   "recommendation": "建议使用 'moderate' 策略"
# }
```

### 示例 3：监控进化过程

```bash
# 查看进化日志
tail -f data/evolution_log.jsonl

# 查看模块性能
python3 scripts/central_evolution_engine.py --status

# 查看特定模块的进化历史
grep "wallet_analysis" data/evolution_log.jsonl | tail -20
```

## 🚀 启动自动进化系统

### 方式 1：后台守护进程

```bash
# 创建启动脚本
cat > start_evolution.sh << 'EOF'
#!/bin/bash
cd ~/.openclaw/workspace/.agents/skills/polymarket-analytics
nohup python3 scripts/evolution_manager.py --run > evolution.log 2>&1 &
echo $! > evolution.pid
echo "自动进化系统已启动 (PID: $(cat evolution.pid))"
EOF

chmod +x start_evolution.sh
./start_evolution.sh

# 停止系统
kill $(cat evolution.pid)
```

### 方式 2：定时任务

```bash
# 添加到 crontab，每小时运行一次进化
crontab -e

# 添加:
0 * * * * cd ~/.openclaw/workspace/.agents/skills/polymarket-analytics && python3 scripts/evolution_manager.py --evolve-now >> evolution_cron.log 2>&1
```

### 方式 3：手动触发

```bash
# 按需手动触发进化
python3 scripts/evolution_manager.py --evolve-now
```

## 📈 预期进化效果

### 短期效果（1-2周）
- 识别最有效的分析指标
- 优化基础参数配置
- 建立初步的进化规则库

### 中期效果（1-2月）
- 显著提升分析准确度
- 形成个性化的策略推荐
- 自动适应市场变化

### 长期效果（3月+）
- 高度优化的分析系统
- 持续自我改进的能力
- 超越人工调优的效果

## ⚠️ 注意事项

1. **进化需要时间积累数据**
   - 建议至少运行20-30次后再评估效果
   - 初期可能效果不明显

2. **避免过度进化**
   - 设置合理的进化频率
   - 保留一定的稳定性

3. **监控进化过程**
   - 定期检查进化日志
   - 关注性能指标变化

4. **备份重要配置**
   - 定期备份 `data/*_evolved.json`
   - 防止意外丢失优化成果

## 🔧 高级配置

### 自定义进化参数

编辑 `data/meta_evolution.json`:

```json
{
  "evolution_frequency": 10,
  "selection_pressure": 0.7,
  "mutation_rate": 0.1,
  "convergence_criteria": {
    "max_generations": 100,
    "improvement_threshold": 0.01
  }
}
```

### 添加自定义进化规则

编辑 `data/evolution_rules.json`:

```json
[
  {
    "rule_id": "custom_001",
    "module": "wallet_analysis",
    "condition": "win_rate > 70",
    "action": "增加权重至0.4",
    "success_rate": 85.5
  }
]
```

## 📚 相关文档

- `SKILL.md` - 技能主文档
- `README.md` - 使用指南
- `copy_trade_strategy_top1.md` - 跟单策略文档

---

**现在整个 Polymarket Analytics Skill 具备了完整的自我进化能力！** 🧬🚀
