#!/usr/bin/env python3
"""
Polymarket 策略自我进化工具
功能：根据回测结果自动优化策略参数
"""

import argparse
import json
import os
from datetime import datetime
from typing import Dict, List
import statistics

class StrategyEvolver:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.expanduser("~/.openclaw/workspace/.agents/skills/polymarket-analytics/data")
        
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.strategy_file = os.path.join(data_dir, "strategies.json")
        self.backtest_dir = os.path.join(data_dir, "backtest_results")
        os.makedirs(self.backtest_dir, exist_ok=True)
        
        # 默认策略模板
        self.default_strategy = {
            'name': 'default',
            'version': 1,
            'created_at': datetime.now().isoformat(),
            'parameters': {
                'position_size': 0.10,  # 10%
                'stop_loss': 0.20,      # 20%
                'take_profit': 0.50,    # 50%
                'min_liquidity': 20000,
                'max_positions': 10,
                'rebalance_threshold': 0.05
            },
            'performance': {
                'total_backtests': 0,
                'avg_return': 0,
                'avg_sharpe': 0,
                'avg_drawdown': 0,
                'win_rate': 0
            }
        }
    
    def load_strategies(self) -> Dict:
        """加载策略库"""
        if os.path.exists(self.strategy_file):
            with open(self.strategy_file, 'r') as f:
                return json.load(f)
        return {'strategies': [self.default_strategy], 'active': 'default'}
    
    def save_strategies(self, strategies: Dict):
        """保存策略库"""
        with open(self.strategy_file, 'w') as f:
            json.dump(strategies, f, indent=2)
    
    def load_backtest_result(self, result_file: str) -> Dict:
        """加载回测结果"""
        if not os.path.exists(result_file):
            # 尝试从 backtest_results 目录找
            result_file = os.path.join(self.backtest_dir, result_file)
        
        with open(result_file, 'r') as f:
            return json.load(f)
    
    def evaluate_performance(self, result: Dict) -> Dict:
        """评估回测表现"""
        return {
            'total_return': result.get('total_return', 0),
            'sharpe_ratio': result.get('sharpe_ratio', 0),
            'max_drawdown': result.get('max_drawdown', 0),
            'win_rate': result.get('win_rate', 0),
            'score': self.calculate_score(result)
        }
    
    def calculate_score(self, result: Dict) -> float:
        """计算综合评分"""
        total_return = result.get('total_return', 0)
        sharpe = result.get('sharpe_ratio', 0)
        drawdown = result.get('max_drawdown', 0)
        win_rate = result.get('win_rate', 0)
        
        # 综合评分公式
        # 收益权重40%，夏普30%，回撤20%，胜率10%
        score = (
            total_return * 0.4 +
            sharpe * 10 * 0.3 +  # 夏普比率通常<3，放大
            (100 - drawdown) * 0.2 +  # 回撤越小越好
            win_rate * 0.1
        )
        
        return round(score, 2)
    
    def generate_variants(self, strategy: Dict, num_variants: int = 5) -> List[Dict]:
        """生成策略变体"""
        params = strategy['parameters'].copy()
        variants = []
        
        # 参数调整范围
        adjustments = [
            {'position_size': 0.05, 'stop_loss': 0.15, 'take_profit': 0.40},
            {'position_size': 0.15, 'stop_loss': 0.25, 'take_profit': 0.60},
            {'position_size': 0.08, 'stop_loss': 0.18, 'take_profit': 0.45},
            {'position_size': 0.12, 'stop_loss': 0.22, 'take_profit': 0.55},
            {'position_size': 0.10, 'stop_loss': 0.20, 'take_profit': 0.50, 'min_liquidity': 30000}
        ]
        
        for i, adj in enumerate(adjustments[:num_variants]):
            variant = strategy.copy()
            variant['name'] = f"{strategy['name']}_v{strategy['version']+1}_{i+1}"
            variant['version'] = strategy['version'] + 1
            variant['parent'] = strategy['name']
            variant['created_at'] = datetime.now().isoformat()
            variant['parameters'] = {**params, **adj}
            variant['performance'] = {
                'total_backtests': 0,
                'avg_return': 0,
                'avg_sharpe': 0,
                'avg_drawdown': 0,
                'win_rate': 0
            }
            variants.append(variant)
        
        return variants
    
    def evolve_strategy(self, backtest_file: str = None, target: str = 'sharpe_ratio') -> Dict:
        """执行策略进化"""
        print("🧬 开始策略进化...")
        print()
        
        # 加载现有策略
        strategies = self.load_strategies()
        active_strategy = None
        
        for s in strategies['strategies']:
            if s['name'] == strategies['active']:
                active_strategy = s
                break
        
        if not active_strategy:
            active_strategy = self.default_strategy
        
        print(f"📋 当前策略: {active_strategy['name']} (v{active_strategy['version']})")
        print(f"   参数: {json.dumps(active_strategy['parameters'], indent=2)}")
        print()
        
        # 如果有回测结果，评估表现
        if backtest_file:
            print(f"📊 加载回测结果: {backtest_file}")
            result = self.load_backtest_result(backtest_file)
            perf = self.evaluate_performance(result)
            
            print(f"   评分: {perf['score']}")
            print(f"   收益: {perf['total_return']}%")
            print(f"   夏普: {perf['sharpe_ratio']}")
            print(f"   回撤: {perf['max_drawdown']}%")
            print()
            
            # 更新策略表现记录
            active_strategy['performance']['total_backtests'] += 1
            
            # 计算移动平均
            n = active_strategy['performance']['total_backtests']
            old_avg = active_strategy['performance']['avg_return']
            active_strategy['performance']['avg_return'] = round(
                (old_avg * (n-1) + perf['total_return']) / n, 2
            ) if n > 0 else perf['total_return']
            
            old_sharpe = active_strategy['performance']['avg_sharpe']
            active_strategy['performance']['avg_sharpe'] = round(
                (old_sharpe * (n-1) + perf['sharpe_ratio']) / n, 2
            ) if n > 0 else perf['sharpe_ratio']
        
        # 生成变体
        print("🎲 生成策略变体...")
        variants = self.generate_variants(active_strategy, num_variants=3)
        
        for i, v in enumerate(variants, 1):
            print(f"   变体 {i}: {v['name']}")
            print(f"      仓位: {v['parameters']['position_size']*100}%")
            print(f"      止损: {v['parameters']['stop_loss']*100}%")
            print(f"      止盈: {v['parameters']['take_profit']*100}%")
        
        # 添加到策略库
        strategies['strategies'].extend(variants)
        
        # 保存
        self.save_strategies(strategies)
        
        print()
        print("✅ 策略进化完成！")
        print(f"   新增 {len(variants)} 个策略变体")
        print(f"   策略库总数: {len(strategies['strategies'])}")
        
        return {
            'parent_strategy': active_strategy['name'],
            'new_variants': [v['name'] for v in variants],
            'recommendation': f"建议测试变体: {variants[0]['name']}"
        }
    
    def select_best_strategy(self) -> Dict:
        """选择最佳策略"""
        strategies = self.load_strategies()
        
        best = None
        best_score = -999
        
        for s in strategies['strategies']:
            perf = s.get('performance', {})
            score = (
                perf.get('avg_return', 0) * 0.4 +
                perf.get('avg_sharpe', 0) * 10 * 0.3 +
                (100 - perf.get('avg_drawdown', 0)) * 0.2 +
                perf.get('win_rate', 0) * 0.1
            )
            
            if score > best_score and perf.get('total_backtests', 0) > 0:
                best_score = score
                best = s
        
        return best
    
    def list_strategies(self) -> List[Dict]:
        """列出所有策略"""
        strategies = self.load_strategies()
        return strategies['strategies']
    
    def format_output(self, result: Dict, format_type: str = 'text') -> str:
        """格式化输出"""
        if format_type == 'telegram':
            output = f"🧬 <b>策略进化完成</b>\n\n"
            output += f"👨‍👩‍👧‍👦 父策略: {result['parent_strategy']}\n"
            output += f"🆕 新变体数量: {len(result['new_variants'])}\n\n"
            output += f"📝 <b>新策略变体</b>\n"
            for i, name in enumerate(result['new_variants'], 1):
                output += f"{i}. {name}\n"
            output += f"\n💡 <b>建议</b>: {result['recommendation']}"
        else:
            output = f"🧬 策略进化报告\n"
            output += f"{'='*50}\n\n"
            output += f"父策略: {result['parent_strategy']}\n"
            output += f"新变体: {', '.join(result['new_variants'])}\n"
            output += f"建议: {result['recommendation']}\n"
        
        return output

def main():
    parser = argparse.ArgumentParser(description='Polymarket 策略进化工具')
    parser.add_argument('--backtest-file', '-b', help='回测结果文件')
    parser.add_argument('--optimize-target', '-t', 
                        choices=['sharpe_ratio', 'return', 'drawdown', 'win_rate'],
                        default='sharpe_ratio', help='优化目标')
    parser.add_argument('--list', '-l', action='store_true', help='列出所有策略')
    parser.add_argument('--select-best', '-s', action='store_true', help='选择最佳策略')
    parser.add_argument('--output-format', '-f', 
                        choices=['text', 'telegram', 'json'],
                        default='text')
    
    args = parser.parse_args()
    
    evolver = StrategyEvolver()
    
    if args.list:
        strategies = evolver.list_strategies()
        print(f"📋 策略库 ({len(strategies)} 个策略):\n")
        for s in strategies:
            perf = s.get('performance', {})
            print(f"  • {s['name']} (v{s['version']})")
            print(f"    回测次数: {perf.get('total_backtests', 0)}")
            print(f"    平均收益: {perf.get('avg_return', 0)}%")
            print(f"    平均夏普: {perf.get('avg_sharpe', 0)}")
            print()
        return
    
    if args.select_best:
        best = evolver.select_best_strategy()
        if best:
            print(f"🏆 最佳策略: {best['name']}")
            print(f"   参数: {json.dumps(best['parameters'], indent=2)}")
            print(f"   表现: {json.dumps(best['performance'], indent=2)}")
        else:
            print("❌ 未找到有回测记录的策略")
        return
    
    # 执行进化
    result = evolver.evolve_strategy(args.backtest_file, args.optimize_target)
    
    if args.output_format == 'json':
        print(json.dumps(result, indent=2))
    else:
        print(evolver.format_output(result, args.output_format))

if __name__ == '__main__':
    main()
