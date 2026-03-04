#!/usr/bin/env python3
"""
模拟回测模块 - 进化适配器
功能：动态优化回测参数和策略
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from central_evolution_engine import CentralEvolutionEngine

class EvolvableBacktester:
    """可进化的回测器"""
    
    def __init__(self):
        self.engine = CentralEvolutionEngine()
        self.config = self.load_evolved_config()
        self.backtest_count = 0
        self.results_history = []
        
    def load_evolved_config(self) -> Dict:
        """加载进化后的配置"""
        config_file = os.path.join(
            os.path.expanduser("~/.openclaw/workspace/.agents/skills/polymarket-analytics/data"),
            "backtesting_evolved.json"
        )
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        
        # 默认配置
        return {
            'optimal_params': {
                'position_size': 100,
                'stop_loss': 0.15,
                'take_profit': 0.30,
                'fee_rate': 0.02
            },
            'strategies': [
                {'name': 'conservative', 'position_multiplier': 0.5, 'stop_loss': 0.10},
                {'name': 'moderate', 'position_multiplier': 1.0, 'stop_loss': 0.15},
                {'name': 'aggressive', 'position_multiplier': 1.5, 'stop_loss': 0.20}
            ],
            'risk_management': {
                'max_position_per_market': 0.1,
                'max_total_exposure': 0.5,
                'daily_loss_limit': 0.1
            }
        }
    
    def run_backtest(self, target_address: str, days: int = 90, 
                     initial_capital: float = 1000, 
                     strategy: str = 'moderate') -> Dict:
        """
        进化版回测
        使用优化后的参数和策略
        """
        import time
        start_time = time.time()
        
        # 获取策略配置
        strategy_config = self.get_strategy_config(strategy)
        
        # 调整参数
        position_size = initial_capital * strategy_config['position_multiplier'] * \
                       self.config['optimal_params']['position_size'] / 100
        
        stop_loss = strategy_config.get('stop_loss', 0.15)
        take_profit = self.config['optimal_params']['take_profit']
        
        # 执行基础回测
        from backtesting import PolymarketBacktester
        base_backtester = PolymarketBacktester()
        
        result = base_backtester.run_backtest(
            target_address, 
            days, 
            initial_capital,
            position_size
        )
        
        execution_time = time.time() - start_time
        
        # 应用进化后的分析
        if result:
            result = self.enhance_result(result, strategy)
            self.record_backtest(target_address, result, execution_time, strategy)
            
            # 触发进化检查
            self.backtest_count += 1
            if self.backtest_count % 5 == 0:  # 每5次回测触发进化
                self.trigger_evolution()
        
        return result
    
    def get_strategy_config(self, strategy_name: str) -> Dict:
        """获取策略配置"""
        strategies = self.config.get('strategies', [])
        for s in strategies:
            if s['name'] == strategy_name:
                return s
        return {'position_multiplier': 1.0, 'stop_loss': 0.15}
    
    def enhance_result(self, result: Dict, strategy: str) -> Dict:
        """增强回测结果"""
        # 计算风险调整收益
        total_return = result.get('total_return', 0)
        max_drawdown = result.get('max_drawdown', 0)
        sharpe = result.get('sharpe_ratio', 0)
        
        # 风险调整评分
        if max_drawdown > 0:
            risk_adjusted_return = total_return / (1 + max_drawdown / 100)
        else:
            risk_adjusted_return = total_return
        
        # 综合评分
        composite_score = (
            total_return * 0.4 +
            sharpe * 20 * 0.3 +
            (100 - max_drawdown) * 0.2 +
            risk_adjusted_return * 0.1
        )
        
        result['risk_adjusted_return'] = round(risk_adjusted_return, 2)
        result['composite_score'] = round(composite_score, 2)
        result['strategy_used'] = strategy
        result['parameter_optimization'] = self.config['optimal_params']
        
        # 评级
        if composite_score > 80:
            result['rating'] = "A+"
        elif composite_score > 60:
            result['rating'] = "A"
        elif composite_score > 40:
            result['rating'] = "B"
        elif composite_score > 20:
            result['rating'] = "C"
        else:
            result['rating'] = "D"
        
        return result
    
    def record_backtest(self, address: str, result: Dict, execution_time: float, strategy: str):
        """记录回测结果"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'address': address,
            'strategy': strategy,
            'total_return': result.get('total_return', 0),
            'sharpe_ratio': result.get('sharpe_ratio', 0),
            'max_drawdown': result.get('max_drawdown', 0),
            'composite_score': result.get('composite_score', 0),
            'rating': result.get('rating', 'N/A'),
            'execution_time': execution_time
        }
        
        self.results_history.append(record)
        
        # 保存历史
        history_file = os.path.join(
            os.path.expanduser("~/.openclaw/workspace/.agents/skills/polymarket-analytics/data"),
            "backtest_history.jsonl"
        )
        
        with open(history_file, 'a') as f:
            f.write(json.dumps(record) + '\n')
        
        # 更新引擎性能
        success = result.get('total_return', 0) > 0
        self.engine.update_module_performance(
            'backtesting',
            success,
            execution_time,
            {'address': address, 'score': record['composite_score']}
        )
    
    def trigger_evolution(self):
        """触发进化"""
        print("🧬 触发回测模块进化...")
        self.engine.evolve_backtesting()
        self.config = self.load_evolved_config()
        print("✅ 进化完成，已更新策略参数")
    
    def compare_strategies(self, address: str, days: int = 90) -> Dict:
        """比较不同策略的效果"""
        strategies = ['conservative', 'moderate', 'aggressive']
        results = {}
        
        for strategy in strategies:
            result = self.run_backtest(address, days, strategy=strategy)
            results[strategy] = {
                'return': result.get('total_return', 0),
                'sharpe': result.get('sharpe_ratio', 0),
                'drawdown': result.get('max_drawdown', 0),
                'score': result.get('composite_score', 0),
                'rating': result.get('rating', 'N/A')
            }
        
        # 找出最佳策略
        best_strategy = max(results.items(), key=lambda x: x[1]['score'])
        
        return {
            'comparison': results,
            'best_strategy': best_strategy[0],
            'recommendation': f"建议使用 '{best_strategy[0]}' 策略"
        }
    
    def get_performance_insights(self) -> Dict:
        """获取性能洞察"""
        if not self.results_history:
            return {}
        
        returns = [r['total_return'] for r in self.results_history]
        sharpes = [r['sharpe_ratio'] for r in self.results_history]
        
        return {
            'total_backtests': len(self.results_history),
            'profitable_backtests': len([r for r in self.results_history if r['total_return'] > 0]),
            'avg_return': sum(returns) / len(returns),
            'avg_sharpe': sum(sharpes) / len(sharpes),
            'best_result': max(self.results_history, key=lambda x: x['composite_score']),
            'current_config': self.config
        }

def main():
    """测试进化版回测"""
    import argparse
    
    parser = argparse.ArgumentParser(description='进化版回测')
    parser.add_argument('--target', '-t', required=True, help='目标地址')
    parser.add_argument('--days', '-d', type=int, default=90, help='回测天数')
    parser.add_argument('--strategy', '-s', choices=['conservative', 'moderate', 'aggressive'],
                        default='moderate', help='策略类型')
    parser.add_argument('--capital', '-c', type=float, default=1000, help='初始资金')
    parser.add_argument('--compare', action='store_true', help='比较所有策略')
    parser.add_argument('--insights', action='store_true', help='显示性能洞察')
    
    args = parser.parse_args()
    
    backtester = EvolvableBacktester()
    
    if args.insights:
        insights = backtester.get_performance_insights()
        print(json.dumps(insights, indent=2))
    elif args.compare:
        comparison = backtester.compare_strategies(args.target, args.days)
        print(json.dumps(comparison, indent=2))
    else:
        result = backtester.run_backtest(args.target, args.days, args.capital, args.strategy)
        print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
