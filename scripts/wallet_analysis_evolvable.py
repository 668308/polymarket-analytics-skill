#!/usr/bin/env python3
"""
钱包分析模块 - 进化适配器
功能：与中央进化引擎集成，实现自动优化
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

# 导入中央进化引擎
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from central_evolution_engine import CentralEvolutionEngine

class EvolvableWalletAnalyzer:
    """可进化的钱包分析器"""
    
    def __init__(self):
        self.engine = CentralEvolutionEngine()
        self.config = self.load_evolved_config()
        self.analysis_count = 0
        self.results_history = []
        
    def load_evolved_config(self) -> Dict:
        """加载进化后的配置"""
        config_file = os.path.join(
            os.path.expanduser("~/.openclaw/workspace/.agents/skills/polymarket-analytics/data"),
            "wallet_analysis_evolved.json"
        )
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        
        # 默认配置
        return {
            'weights': {
                'win_rate': 0.25,
                'sharpe_ratio': 0.25,
                'max_drawdown': 0.20,
                'profit_factor': 0.15,
                'consistency': 0.15
            },
            'thresholds': {
                'min_win_rate': 55,
                'min_sharpe': 1.0,
                'max_drawdown': 20
            }
        }
    
    def analyze_wallet(self, address: str, days: int = 90) -> Dict:
        """
        进化版钱包分析
        使用优化后的权重和阈值
        """
        import time
        start_time = time.time()
        
        # 执行基础分析（复用原有代码）
        from wallet_analysis import PolymarketWalletAnalyzer
        base_analyzer = PolymarketWalletAnalyzer()
        result = base_analyzer.analyze_wallet(address, days)
        
        execution_time = time.time() - start_time
        
        # 应用进化后的权重计算综合得分
        if result:
            result = self.apply_evolved_scoring(result)
            
            # 记录分析结果
            self.record_analysis(address, result, execution_time)
            
            # 触发进化检查
            self.analysis_count += 1
            if self.analysis_count % 10 == 0:  # 每10次分析触发进化
                self.trigger_evolution()
        
        return result
    
    def apply_evolved_scoring(self, result: Dict) -> Dict:
        """应用进化后的评分"""
        weights = self.config.get('weights', {})
        thresholds = self.config.get('thresholds', {})
        
        summary = result.get('summary', {})
        
        # 计算加权得分
        score = 0
        score += summary.get('win_rate', 0) * weights.get('win_rate', 0.25)
        score += summary.get('sharpe_ratio', 0) * 10 * weights.get('sharpe_ratio', 0.25)  # 放大夏普比率
        score += (100 - summary.get('max_drawdown', 0)) * weights.get('max_drawdown', 0.20)
        
        # 检查是否达到阈值
        meets_thresholds = (
            summary.get('win_rate', 0) >= thresholds.get('min_win_rate', 55) and
            summary.get('sharpe_ratio', 0) >= thresholds.get('min_sharpe', 1.0) and
            summary.get('max_drawdown', 0) <= thresholds.get('max_drawdown', 20)
        )
        
        result['evolved_score'] = round(score, 2)
        result['meets_thresholds'] = meets_thresholds
        result['recommendation'] = self.generate_recommendation(score, meets_thresholds)
        
        return result
    
    def generate_recommendation(self, score: float, meets_thresholds: bool) -> str:
        """生成进化后的建议"""
        if score > 80 and meets_thresholds:
            return "🌟 顶级交易者 - 强烈推荐跟随"
        elif score > 65 and meets_thresholds:
            return "✅ 优秀交易者 - 建议跟随"
        elif score > 50:
            return "🟡 一般交易者 - 谨慎考虑"
        else:
            return "❌ 不建议跟随 - 风险较高"
    
    def record_analysis(self, address: str, result: Dict, execution_time: float):
        """记录分析结果"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'address': address,
            'score': result.get('evolved_score', 0),
            'meets_thresholds': result.get('meets_thresholds', False),
            'execution_time': execution_time,
            'win_rate': result.get('summary', {}).get('win_rate', 0),
            'sharpe': result.get('summary', {}).get('sharpe_ratio', 0),
            'pnl': result.get('pnl', {}).get('total', 0)
        }
        
        self.results_history.append(record)
        
        # 保存到历史文件
        history_file = os.path.join(
            os.path.expanduser("~/.openclaw/workspace/.agents/skills/polymarket-analytics/data"),
            "wallet_analysis_history.jsonl"
        )
        
        with open(history_file, 'a') as f:
            f.write(json.dumps(record) + '\n')
        
        # 更新中央引擎性能数据
        success = result.get('meets_thresholds', False)
        self.engine.update_module_performance(
            'wallet_analysis',
            success,
            execution_time,
            {'address': address, 'score': record['score']}
        )
    
    def trigger_evolution(self):
        """触发进化"""
        print("🧬 触发钱包分析模块进化...")
        self.engine.evolve_wallet_analysis()
        # 重新加载配置
        self.config = self.load_evolved_config()
        print("✅ 进化完成，已更新配置")
    
    def get_learning_insights(self) -> Dict:
        """获取学习洞察"""
        if not self.results_history:
            return {}
        
        successful = [r for r in self.results_history if r['meets_thresholds']]
        
        return {
            'total_analyzed': len(self.results_history),
            'successful_identified': len(successful),
            'success_rate': len(successful) / len(self.results_history) * 100,
            'avg_score': sum(r['score'] for r in self.results_history) / len(self.results_history),
            'avg_execution_time': sum(r['execution_time'] for r in self.results_history) / len(self.results_history),
            'current_config': self.config
        }

def main():
    """测试进化版钱包分析"""
    import argparse
    
    parser = argparse.ArgumentParser(description='进化版钱包分析')
    parser.add_argument('--address', '-a', required=True, help='钱包地址')
    parser.add_argument('--days', '-d', type=int, default=90, help='分析天数')
    parser.add_argument('--insights', action='store_true', help='显示学习洞察')
    
    args = parser.parse_args()
    
    analyzer = EvolvableWalletAnalyzer()
    
    if args.insights:
        insights = analyzer.get_learning_insights()
        print(json.dumps(insights, indent=2))
    else:
        result = analyzer.analyze_wallet(args.address, args.days)
        print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
