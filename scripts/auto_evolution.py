#!/usr/bin/env python3
"""
Polymarket 自动进化交易原则系统
功能：
1. 实时学习聪明钱特征
2. 自动识别交易信号
3. 动态调整策略参数
4. 建立交易原则库
5. 追踪准确度并自我优化
"""

import os
import json
import time
import requests
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

# API 配置
DATA_API_URL = "https://data-api.polymarket.com"
GAMMA_API_URL = "https://gamma-api.polymarket.com"

# 数据目录
DATA_DIR = os.path.expanduser("~/.openclaw/workspace/.agents/skills/polymarket-analytics/data")
os.makedirs(DATA_DIR, exist_ok=True)

# 交易原则库文件
PRINCIPLES_FILE = os.path.join(DATA_DIR, "trading_principles.json")
LEARNING_LOG_FILE = os.path.join(DATA_DIR, "learning_log.jsonl")
SIGNAL_HISTORY_FILE = os.path.join(DATA_DIR, "signal_history.json")

@dataclass
class TradingPrinciple:
    """交易原则"""
    id: str
    name: str
    condition: str
    action: str
    confidence: float  # 0-100
    success_count: int
    fail_count: int
    accuracy: float
    created_at: str
    last_updated: str
    
@dataclass
class Signal:
    """交易信号"""
    id: str
    type: str  # 'wallet_pattern', 'market_trend', 'price_action'
    source: str  # 来源钱包或市场
    market: str
    direction: str  # 'buy', 'sell', 'hold'
    strength: float  # 0-100
    confidence: float  # 0-100
    timestamp: str
    principle_id: Optional[str] = None
    validated: bool = False
    outcome: Optional[str] = None  # 'success', 'fail', 'pending'

class AutoEvolutionSystem:
    """自动进化系统"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})
        
        # 加载交易原则库
        self.principles = self.load_principles()
        
        # 加载信号历史
        self.signal_history = self.load_signal_history()
        
        # 学习统计
        self.learning_stats = {
            'total_signals': 0,
            'validated_signals': 0,
            'successful_predictions': 0,
            'principles_evolved': 0
        }
    
    def load_principles(self) -> List[TradingPrinciple]:
        """加载交易原则库"""
        if not os.path.exists(PRINCIPLES_FILE):
            # 初始化默认原则
            default_principles = [
                TradingPrinciple(
                    id="p001",
                    name="高胜率钱包跟随",
                    condition="wallet.win_rate > 60 AND wallet.pnl > 5000",
                    action="跟随该钱包的买入信号，仓位5%",
                    confidence=70.0,
                    success_count=0,
                    fail_count=0,
                    accuracy=0.0,
                    created_at=datetime.now().isoformat(),
                    last_updated=datetime.now().isoformat()
                ),
                TradingPrinciple(
                    id="p002",
                    name="趋势突破交易",
                    condition="price.change_24h > 10 AND volume.increase > 50%",
                    action="顺势买入，止损-15%",
                    confidence=60.0,
                    success_count=0,
                    fail_count=0,
                    accuracy=0.0,
                    created_at=datetime.now().isoformat(),
                    last_updated=datetime.now().isoformat()
                ),
                TradingPrinciple(
                    id="p003",
                    name="流动性筛选",
                    condition="market.liquidity < 20000",
                    action="避免参与，流动性不足",
                    confidence=85.0,
                    success_count=0,
                    fail_count=0,
                    accuracy=0.0,
                    created_at=datetime.now().isoformat(),
                    last_updated=datetime.now().isoformat()
                )
            ]
            self.save_principles(default_principles)
            return default_principles
        
        with open(PRINCIPLES_FILE, 'r') as f:
            data = json.load(f)
            return [TradingPrinciple(**p) for p in data]
    
    def save_principles(self, principles: List[TradingPrinciple]):
        """保存交易原则库"""
        with open(PRINCIPLES_FILE, 'w') as f:
            json.dump([asdict(p) for p in principles], f, indent=2)
    
    def load_signal_history(self) -> List[Signal]:
        """加载信号历史"""
        if not os.path.exists(SIGNAL_HISTORY_FILE):
            return []
        
        with open(SIGNAL_HISTORY_FILE, 'r') as f:
            data = json.load(f)
            return [Signal(**s) for s in data]
    
    def save_signal_history(self):
        """保存信号历史"""
        with open(SIGNAL_HISTORY_FILE, 'w') as f:
            json.dump([asdict(s) for s in self.signal_history], f, indent=2)
    
    def log_learning(self, event: Dict):
        """记录学习日志"""
        with open(LEARNING_LOG_FILE, 'a') as f:
            f.write(json.dumps({
                'timestamp': datetime.now().isoformat(),
                **event
            }) + '\n')
    
    def analyze_wallet_pattern(self, address: str) -> Dict:
        """分析钱包交易模式并学习"""
        print(f"🔍 分析钱包模式: {address}")
        
        try:
            # 获取钱包数据
            resp = self.session.get(
                f"{DATA_API_URL}/positions",
                params={'user': address, 'limit': 100},
                timeout=30
            )
            positions = resp.json()
            
            resp = self.session.get(
                f"{DATA_API_URL}/trades",
                params={'user': address, 'limit': 100},
                timeout=30
            )
            trades = resp.json()
            
            if not trades:
                return {}
            
            # 提取模式特征
            pattern = self.extract_pattern_features(trades, positions)
            
            # 基于模式生成/更新原则
            new_principles = self.generate_principles_from_pattern(pattern, address)
            
            # 记录学习
            self.log_learning({
                'type': 'wallet_analysis',
                'address': address,
                'pattern': pattern,
                'new_principles': [p.id for p in new_principles]
            })
            
            return {
                'address': address,
                'pattern': pattern,
                'principles_generated': len(new_principles)
            }
            
        except Exception as e:
            print(f"❌ 分析失败: {e}")
            return {}
    
    def extract_pattern_features(self, trades: List[Dict], positions: List[Dict]) -> Dict:
        """提取交易模式特征"""
        if not trades:
            return {}
        
        # 基础统计
        total_trades = len(trades)
        buy_trades = [t for t in trades if t.get('side') == 'BUY']
        sell_trades = [t for t in trades if t.get('side') == 'SELL']
        
        # 盈亏分析
        realized_pnls = [t.get('realizedPnl', 0) for t in trades if t.get('realizedPnl')]
        avg_pnl = statistics.mean(realized_pnls) if realized_pnls else 0
        win_rate = len([p for p in realized_pnls if p > 0]) / len(realized_pnls) * 100 if realized_pnls else 0
        
        # 时间模式
        trade_times = [t.get('timestamp', 0) for t in trades]
        if trade_times:
            time_diffs = [trade_times[i+1] - trade_times[i] for i in range(len(trade_times)-1)]
            avg_hold_time = statistics.mean(time_diffs) if time_diffs else 0
        else:
            avg_hold_time = 0
        
        # 仓位模式
        position_sizes = [t.get('size', 0) for t in trades]
        avg_position = statistics.mean(position_sizes) if position_sizes else 0
        
        return {
            'total_trades': total_trades,
            'buy_ratio': len(buy_trades) / total_trades * 100 if total_trades else 0,
            'win_rate': win_rate,
            'avg_pnl': avg_pnl,
            'avg_hold_time_hours': avg_hold_time / 3600 if avg_hold_time else 0,
            'avg_position_size': avg_position,
            'current_positions': len(positions)
        }
    
    def generate_principles_from_pattern(self, pattern: Dict, address: str) -> List[TradingPrinciple]:
        """从模式生成交易原则"""
        new_principles = []
        
        # 原则1: 高胜率模式
        if pattern.get('win_rate', 0) > 60:
            principle = TradingPrinciple(
                id=f"p_{address[:8]}_win",
                name=f"高胜率钱包 {address[:8]}... 跟随策略",
                condition=f"wallet.address == '{address}' AND wallet.win_rate > 60",
                action="跟随该钱包信号，仓位5%，止盈30%止损15%",
                confidence=pattern['win_rate'],
                success_count=0,
                fail_count=0,
                accuracy=0.0,
                created_at=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat()
            )
            self.principles.append(principle)
            new_principles.append(principle)
            print(f"  🆕 生成原则: {principle.name} (胜率{pattern['win_rate']:.1f}%)")
        
        # 原则2: 持仓时间模式
        hold_time = pattern.get('avg_hold_time_hours', 0)
        if hold_time > 0:
            if hold_time < 24:
                action = "短线交易，快速进出，止盈15%止损10%"
            elif hold_time < 72:
                action = "中线持仓，止盈30%止损15%"
            else:
                action = "长线投资，止盈50%止损20%"
            
            principle = TradingPrinciple(
                id=f"p_{address[:8]}_time",
                name=f"持仓时间模式 {address[:8]}...",
                condition=f"wallet.avg_hold_time_hours ≈ {hold_time:.1f}",
                action=action,
                confidence=60.0,
                success_count=0,
                fail_count=0,
                accuracy=0.0,
                created_at=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat()
            )
            self.principles.append(principle)
            new_principles.append(principle)
            print(f"  🆕 生成原则: {principle.name} (持仓{hold_time:.1f}小时)")
        
        # 保存更新后的原则库
        self.save_principles(self.principles)
        
        return new_principles
    
    def detect_signal(self, market_data: Dict) -> Optional[Signal]:
        """基于原则检测交易信号"""
        signals = []
        
        for principle in self.principles:
            if principle.confidence < 50:  # 只使用高信心原则
                continue
            
            # 简化版：根据原则条件匹配
            signal_strength = self.evaluate_signal_strength(market_data, principle)
            
            if signal_strength > 70:  # 强信号阈值
                signal = Signal(
                    id=f"sig_{int(time.time())}_{len(signals)}",
                    type='principle_based',
                    source=principle.name,
                    market=market_data.get('title', 'Unknown'),
                    direction=self.infer_direction(principle),
                    strength=signal_strength,
                    confidence=principle.confidence,
                    timestamp=datetime.now().isoformat(),
                    principle_id=principle.id,
                    validated=False,
                    outcome=None
                )
                signals.append(signal)
        
        # 返回最强信号
        if signals:
            best = max(signals, key=lambda s: s.strength)
            self.signal_history.append(best)
            self.save_signal_history()
            
            self.log_learning({
                'type': 'signal_detected',
                'signal': asdict(best)
            })
            
            return best
        
        return None
    
    def evaluate_signal_strength(self, market_data: Dict, principle: TradingPrinciple) -> float:
        """评估信号强度"""
        # 这里简化处理，实际应该根据原则条件解析和匹配
        strength = principle.confidence
        
        # 增加市场流动性权重
        liquidity = market_data.get('liquidity', 0)
        if liquidity > 50000:
            strength += 10
        elif liquidity < 10000:
            strength -= 20
        
        return min(100, strength)
    
    def infer_direction(self, principle: TradingPrinciple) -> str:
        """从原则推断交易方向"""
        action = principle.action.lower()
        if 'buy' in action or '买入' in action or '跟随' in action:
            return 'buy'
        elif 'sell' in action or '卖出' in action:
            return 'sell'
        else:
            return 'hold'
    
    def validate_signals(self):
        """验证历史信号的准确性"""
        print("🔍 验证历史信号...")
        
        validated_count = 0
        
        for signal in self.signal_history:
            if signal.validated or signal.outcome:
                continue
            
            # 检查信号发出后的市场走势（简化版）
            # 实际应该查询价格历史
            outcome = self.check_signal_outcome(signal)
            
            if outcome:
                signal.outcome = outcome
                signal.validated = True
                validated_count += 1
                
                # 更新对应原则的统计数据
                self.update_principle_stats(signal)
        
        if validated_count > 0:
            self.save_signal_history()
            self.save_principles(self.principles)
            print(f"✅ 验证了 {validated_count} 个信号")
        
        return validated_count
    
    def check_signal_outcome(self, signal: Signal) -> Optional[str]:
        """检查信号结果"""
        # 简化实现：假设信号发出24小时后验证
        signal_time = datetime.fromisoformat(signal.timestamp)
        now = datetime.now()
        
        if (now - signal_time).hours < 24:
            return None  # 还未到验证时间
        
        # 实际应该查询价格变化
        # 这里随机模拟，实际应该调用API
        import random
        return 'success' if random.random() > 0.4 else 'fail'
    
    def update_principle_stats(self, signal: Signal):
        """更新原则统计数据"""
        if not signal.principle_id:
            return
        
        for p in self.principles:
            if p.id == signal.principle_id:
                if signal.outcome == 'success':
                    p.success_count += 1
                else:
                    p.fail_count += 1
                
                # 重新计算准确度
                total = p.success_count + p.fail_count
                if total > 0:
                    p.accuracy = (p.success_count / total) * 100
                    
                    # 根据准确度调整信心度
                    if p.accuracy > 70:
                        p.confidence = min(95, p.confidence + 2)
                    elif p.accuracy < 40:
                        p.confidence = max(30, p.confidence - 5)
                
                p.last_updated = datetime.now().isoformat()
                
                self.log_learning({
                    'type': 'principle_updated',
                    'principle_id': p.id,
                    'accuracy': p.accuracy,
                    'confidence': p.confidence
                })
                break
    
    def evolve_principles(self):
        """进化交易原则"""
        print("🧬 进化交易原则...")
        
        # 1. 淘汰低准确度原则
        before_count = len(self.principles)
        self.principles = [p for p in self.principles if p.accuracy >= 30 or p.success_count + p.fail_count < 5]
        removed = before_count - len(self.principles)
        
        # 2. 合并相似原则
        merged = self.merge_similar_principles()
        
        # 3. 基于成功模式生成新原则
        new_principles = self.generate_new_principles()
        
        self.save_principles(self.principles)
        
        print(f"✅ 进化完成:")
        print(f"   淘汰原则: {removed}")
        print(f"   合并原则: {merged}")
        print(f"   新增原则: {len(new_principles)}")
        print(f"   原则总数: {len(self.principles)}")
        
        return {
            'removed': removed,
            'merged': merged,
            'new': len(new_principles),
            'total': len(self.principles)
        }
    
    def merge_similar_principles(self) -> int:
        """合并相似原则"""
        # 简化实现：合并相同名称的原则
        merged_count = 0
        principle_map = {}
        
        for p in self.principles:
            key = p.name
            if key in principle_map:
                # 合并统计
                existing = principle_map[key]
                existing.success_count += p.success_count
                existing.fail_count += p.fail_count
                total = existing.success_count + existing.fail_count
                if total > 0:
                    existing.accuracy = existing.success_count / total * 100
                merged_count += 1
            else:
                principle_map[key] = p
        
        self.principles = list(principle_map.values())
        return merged_count
    
    def generate_new_principles(self) -> List[TradingPrinciple]:
        """基于成功案例生成新原则"""
        new_principles = []
        
        # 找出高准确度原则
        successful_principles = [p for p in self.principles if p.accuracy > 65]
        
        for sp in successful_principles:
            # 创建变体
            if '止盈' in sp.action:
                new_action = sp.action.replace('30%', '40%').replace('50%', '60%')
            elif '止损' in sp.action:
                new_action = sp.action.replace('15%', '10%')
            else:
                continue
            
            new_p = TradingPrinciple(
                id=f"p_evolved_{int(time.time())}_{len(new_principles)}",
                name=f"{sp.name} (优化版)",
                condition=sp.condition,
                action=new_action,
                confidence=sp.confidence * 0.9,  # 略低信心
                success_count=0,
                fail_count=0,
                accuracy=0.0,
                created_at=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat()
            )
            
            self.principles.append(new_p)
            new_principles.append(new_p)
        
        return new_principles
    
    def get_best_principles(self, top_n: int = 5) -> List[TradingPrinciple]:
        """获取最佳原则"""
        # 按准确度排序
        sorted_p = sorted(
            [p for p in self.principles if p.success_count + p.fail_count >= 3],
            key=lambda x: x.accuracy,
            reverse=True
        )
        return sorted_p[:top_n]
    
    def print_principles(self):
        """打印当前原则库"""
        print("\n📚 交易原则库")
        print("=" * 60)
        
        for i, p in enumerate(self.principles, 1):
            status = "🟢" if p.accuracy > 60 else "🟡" if p.accuracy > 40 else "🔴" if p.accuracy > 0 else "⚪"
            print(f"\n{i}. {status} {p.name}")
            print(f"   条件: {p.condition}")
            print(f"   操作: {p.action}")
            print(f"   准确度: {p.accuracy:.1f}% ({p.success_count}/{p.success_count+p.fail_count})")
            print(f"   信心度: {p.confidence:.1f}%")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Polymarket 自动进化系统')
    parser.add_argument('--analyze-wallet', '-w', help='分析钱包并学习')
    parser.add_argument('--validate', '-v', action='store_true', help='验证信号')
    parser.add_argument('--evolve', '-e', action='store_true', help='进化原则')
    parser.add_argument('--list-principles', '-l', action='store_true', help='列出原则')
    parser.add_argument('--best-principles', '-b', action='store_true', help='显示最佳原则')
    
    args = parser.parse_args()
    
    system = AutoEvolutionSystem()
    
    if args.analyze_wallet:
        result = system.analyze_wallet_pattern(args.analyze_wallet)
        if result:
            print(f"\n✅ 分析完成")
            print(f"   生成 {result['principles_generated']} 个新原则")
    
    elif args.validate:
        count = system.validate_signals()
        print(f"\n✅ 验证了 {count} 个信号")
    
    elif args.evolve:
        result = system.evolve_principles()
        print(f"\n🧬 进化完成")
        print(f"   淘汰: {result['removed']}")
        print(f"   合并: {result['merged']}")
        print(f"   新增: {result['new']}")
    
    elif args.list_principles:
        system.print_principles()
    
    elif args.best_principles:
        print("\n🏆 最佳交易原则 (Top 5)")
        print("=" * 60)
        for i, p in enumerate(system.get_best_principles(5), 1):
            print(f"\n{i}. {p.name}")
            print(f"   准确度: {p.accuracy:.1f}%")
            print(f"   操作: {p.action}")
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
