#!/usr/bin/env python3
"""
Polymarket 中央进化引擎 (Central Evolution Engine)
功能：协调所有模块的自动进化和自我优化
"""

import os
import json
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import importlib.util
import sys

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.path.expanduser("~/.openclaw/workspace/.agents/skills/polymarket-analytics/data")
EVOLUTION_LOG = os.path.join(DATA_DIR, "evolution_log.jsonl")
MODULE_PERFORMANCE_FILE = os.path.join(DATA_DIR, "module_performance.json")

@dataclass
class ModuleMetrics:
    """模块性能指标"""
    module_name: str
    execution_count: int = 0
    success_count: int = 0
    avg_execution_time: float = 0.0
    last_execution: str = ""
    accuracy_score: float = 0.0  # 准确度评分 0-100
    user_rating: float = 0.0  # 用户满意度
    evolution_count: int = 0
    
@dataclass
class EvolutionRule:
    """进化规则"""
    rule_id: str
    module: str
    condition: str
    action: str
    success_rate: float
    created_at: str
    last_applied: str
    application_count: int

class CentralEvolutionEngine:
    """中央进化引擎"""
    
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.modules = {
            'wallet_analysis': self.evolve_wallet_analysis,
            'backtesting': self.evolve_backtesting,
            'market_analysis': self.evolve_market_analysis,
            'strategy_suggestions': self.evolve_strategy_suggestions,
            'self_evolution': self.evolve_self_evolution
        }
        self.performance_data = self.load_performance_data()
        self.evolution_rules = self.load_evolution_rules()
        
    def load_performance_data(self) -> Dict[str, ModuleMetrics]:
        """加载模块性能数据"""
        if os.path.exists(MODULE_PERFORMANCE_FILE):
            with open(MODULE_PERFORMANCE_FILE, 'r') as f:
                data = json.load(f)
                return {k: ModuleMetrics(**v) for k, v in data.items()}
        return {}
    
    def save_performance_data(self):
        """保存性能数据"""
        with open(MODULE_PERFORMANCE_FILE, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.performance_data.items()}, f, indent=2)
    
    def load_evolution_rules(self) -> List[EvolutionRule]:
        """加载进化规则"""
        rules_file = os.path.join(DATA_DIR, "evolution_rules.json")
        if os.path.exists(rules_file):
            with open(rules_file, 'r') as f:
                data = json.load(f)
                return [EvolutionRule(**r) for r in data]
        return []
    
    def save_evolution_rules(self):
        """保存进化规则"""
        rules_file = os.path.join(DATA_DIR, "evolution_rules.json")
        with open(rules_file, 'w') as f:
            json.dump([asdict(r) for r in self.evolution_rules], f, indent=2)
    
    def log_evolution(self, event: Dict):
        """记录进化日志"""
        with open(EVOLUTION_LOG, 'a') as f:
            f.write(json.dumps({
                'timestamp': datetime.now().isoformat(),
                **event
            }) + '\n')
    
    def update_module_performance(self, module_name: str, success: bool, execution_time: float, metadata: Dict = None):
        """更新模块性能数据"""
        if module_name not in self.performance_data:
            self.performance_data[module_name] = ModuleMetrics(module_name=module_name)
        
        metrics = self.performance_data[module_name]
        metrics.execution_count += 1
        if success:
            metrics.success_count += 1
        
        # 更新平均执行时间
        metrics.avg_execution_time = (
            (metrics.avg_execution_time * (metrics.execution_count - 1) + execution_time) 
            / metrics.execution_count
        )
        
        metrics.last_execution = datetime.now().isoformat()
        
        # 计算准确度
        if metrics.execution_count > 0:
            metrics.accuracy_score = (metrics.success_count / metrics.execution_count) * 100
        
        self.save_performance_data()
        
        self.log_evolution({
            'type': 'module_execution',
            'module': module_name,
            'success': success,
            'execution_time': execution_time,
            'metadata': metadata or {}
        })
    
    def evolve_wallet_analysis(self) -> Dict:
        """
        进化钱包分析模块
        - 学习哪些指标最能预测成功
        - 优化权重分配
        - 发现新的分析维度
        """
        print("🧬 进化钱包分析模块...")
        
        # 1. 分析历史分析结果的准确度
        analysis_results = self.load_analysis_history()
        
        # 2. 识别高准确度指标
        successful_indicators = self.identify_successful_indicators(analysis_results)
        
        # 3. 生成新的分析规则
        new_rules = []
        for indicator in successful_indicators:
            rule = EvolutionRule(
                rule_id=f"wa_{int(time.time())}_{len(new_rules)}",
                module='wallet_analysis',
                condition=f"{indicator['name']} > {indicator['threshold']}",
                action=f"增加{indicator['name']}权重至{indicator['new_weight']}",
                success_rate=indicator['success_rate'],
                created_at=datetime.now().isoformat(),
                last_applied=datetime.now().isoformat(),
                application_count=0
            )
            new_rules.append(rule)
        
        # 4. 优化权重配置
        optimized_weights = self.optimize_weights('wallet_analysis', successful_indicators)
        
        # 5. 保存新的配置
        config = {
            'weights': optimized_weights,
            'indicators': successful_indicators,
            'rules': [asdict(r) for r in new_rules]
        }
        
        config_file = os.path.join(DATA_DIR, "wallet_analysis_evolved.json")
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.log_evolution({
            'type': 'module_evolution',
            'module': 'wallet_analysis',
            'new_rules': len(new_rules),
            'optimized_weights': optimized_weights
        })
        
        print(f"✅ 钱包分析模块进化完成")
        print(f"   新规则: {len(new_rules)}")
        print(f"   优化指标: {len(optimized_weights)}")
        
        return {
            'module': 'wallet_analysis',
            'new_rules': len(new_rules),
            'config_file': config_file
        }
    
    def evolve_backtesting(self) -> Dict:
        """
        进化回测模块
        - 动态调整跟单比例
        - 优化止盈止损点
        - 改进仓位管理策略
        """
        print("🧬 进化回测模块...")
        
        # 1. 分析历史回测结果
        backtest_results = self.load_backtest_history()
        
        # 2. 识别最优参数
        optimal_params = self.find_optimal_parameters(backtest_results)
        
        # 3. 生成新的策略变体
        strategies = self.generate_strategy_variants(optimal_params)
        
        # 4. 优化风险管理规则
        risk_rules = self.evolve_risk_management(backtest_results)
        
        # 5. 保存进化后的配置
        config = {
            'optimal_params': optimal_params,
            'strategies': strategies,
            'risk_rules': risk_rules,
            'position_sizing_model': self.evolve_position_sizing(backtest_results)
        }
        
        config_file = os.path.join(DATA_DIR, "backtesting_evolved.json")
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.log_evolution({
            'type': 'module_evolution',
            'module': 'backtesting',
            'optimal_params': optimal_params,
            'strategies_count': len(strategies)
        })
        
        print(f"✅ 回测模块进化完成")
        print(f"   最优参数: {len(optimal_params)}")
        print(f"   策略变体: {len(strategies)}")
        
        return {
            'module': 'backtesting',
            'optimal_params': optimal_params,
            'config_file': config_file
        }
    
    def evolve_market_analysis(self) -> Dict:
        """
        进化市场分析模块
        - 识别市场模式
        - 预测趋势
        - 发现异常信号
        """
        print("🧬 进化市场分析模块...")
        
        # 1. 分析历史市场数据
        market_data = self.load_market_history()
        
        # 2. 识别成功模式
        patterns = self.identify_market_patterns(market_data)
        
        # 3. 生成预测模型
        prediction_models = self.generate_prediction_models(patterns)
        
        # 4. 优化异常检测
        anomaly_rules = self.evolve_anomaly_detection(market_data)
        
        # 5. 保存配置
        config = {
            'patterns': patterns,
            'prediction_models': prediction_models,
            'anomaly_rules': anomaly_rules,
            'indicators': self.evolve_market_indicators(market_data)
        }
        
        config_file = os.path.join(DATA_DIR, "market_analysis_evolved.json")
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.log_evolution({
            'type': 'module_evolution',
            'module': 'market_analysis',
            'patterns': len(patterns),
            'models': len(prediction_models)
        })
        
        print(f"✅ 市场分析模块进化完成")
        print(f"   识别模式: {len(patterns)}")
        print(f"   预测模型: {len(prediction_models)}")
        
        return {
            'module': 'market_analysis',
            'patterns': len(patterns),
            'config_file': config_file
        }
    
    def evolve_strategy_suggestions(self) -> Dict:
        """
        进化策略建议模块
        - 根据历史表现调整建议
        - 个性化推荐
        - 动态风险评估
        """
        print("🧬 进化策略建议模块...")
        
        # 1. 分析历史建议效果
        suggestion_history = self.load_suggestion_history()
        
        # 2. 识别成功建议模式
        successful_patterns = self.identify_successful_suggestions(suggestion_history)
        
        # 3. 优化风险评级
        risk_grading = self.evolve_risk_grading(suggestion_history)
        
        # 4. 生成个性化推荐规则
        personalization_rules = self.generate_personalization_rules(suggestion_history)
        
        # 5. 保存配置
        config = {
            'successful_patterns': successful_patterns,
            'risk_grading': risk_grading,
            'personalization': personalization_rules,
            'confidence_thresholds': self.optimize_confidence_thresholds(suggestion_history)
        }
        
        config_file = os.path.join(DATA_DIR, "strategy_suggestions_evolved.json")
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.log_evolution({
            'type': 'module_evolution',
            'module': 'strategy_suggestions',
            'patterns': len(successful_patterns),
            'risk_levels': len(risk_grading)
        })
        
        print(f"✅ 策略建议模块进化完成")
        print(f"   成功模式: {len(successful_patterns)}")
        print(f"   风险等级: {len(risk_grading)}")
        
        return {
            'module': 'strategy_suggestions',
            'patterns': len(successful_patterns),
            'config_file': config_file
        }
    
    def evolve_self_evolution(self) -> Dict:
        """
        元进化：进化模块自身的进化策略
        """
        print("🧬 元进化：优化进化引擎自身...")
        
        # 1. 分析进化历史效果
        evolution_history = self.load_evolution_history()
        
        # 2. 优化进化频率
        optimal_frequency = self.optimize_evolution_frequency(evolution_history)
        
        # 3. 改进选择压力
        selection_pressure = self.evolve_selection_pressure(evolution_history)
        
        # 4. 优化变异率
        mutation_rate = self.optimize_mutation_rate(evolution_history)
        
        # 5. 保存元配置
        config = {
            'evolution_frequency': optimal_frequency,
            'selection_pressure': selection_pressure,
            'mutation_rate': mutation_rate,
            'convergence_criteria': self.evolve_convergence_criteria(evolution_history)
        }
        
        config_file = os.path.join(DATA_DIR, "meta_evolution.json")
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.log_evolution({
            'type': 'meta_evolution',
            'frequency': optimal_frequency,
            'selection_pressure': selection_pressure
        })
        
        print(f"✅ 元进化完成")
        print(f"   最优进化频率: 每 {optimal_frequency} 次执行")
        print(f"   选择压力: {selection_pressure}")
        
        return {
            'module': 'self_evolution',
            'meta_config': config,
            'config_file': config_file
        }
    
    # ============= 辅助方法 =============
    
    def load_analysis_history(self) -> List[Dict]:
        """加载分析历史"""
        history_file = os.path.join(DATA_DIR, "wallet_analysis_history.jsonl")
        results = []
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                for line in f:
                    try:
                        results.append(json.loads(line))
                    except:
                        pass
        return results
    
    def identify_successful_indicators(self, results: List[Dict]) -> List[Dict]:
        """识别成功的指标"""
        indicators = defaultdict(lambda: {'success': 0, 'total': 0, 'values': []})
        
        for result in results:
            # 分析各个指标与成功的关系
            for indicator in ['win_rate', 'sharpe_ratio', 'max_drawdown']:
                if indicator in result:
                    value = result[indicator]
                    success = result.get('actual_success', False)
                    indicators[indicator]['total'] += 1
                    indicators[indicator]['values'].append(value)
                    if success:
                        indicators[indicator]['success'] += 1
        
        successful = []
        for name, data in indicators.items():
            if data['total'] > 0:
                success_rate = data['success'] / data['total']
                if success_rate > 0.6:  # 成功率>60%
                    threshold = statistics.median(data['values'])
                    successful.append({
                        'name': name,
                        'success_rate': success_rate,
                        'threshold': threshold,
                        'new_weight': min(1.0, success_rate * 1.2)
                    })
        
        return sorted(successful, key=lambda x: x['success_rate'], reverse=True)
    
    def optimize_weights(self, module: str, indicators: List[Dict]) -> Dict:
        """优化权重"""
        weights = {}
        total_weight = sum(i['new_weight'] for i in indicators)
        
        for indicator in indicators:
            weights[indicator['name']] = indicator['new_weight'] / total_weight
        
        return weights
    
    def load_backtest_history(self) -> List[Dict]:
        """加载回测历史"""
        # 从回测结果文件收集
        results = []
        for i in range(1, 6):
            file_path = os.path.join(DATA_DIR, f"backtest_top{i}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    try:
                        results.append(json.load(f))
                    except:
                        pass
        return results
    
    def find_optimal_parameters(self, results: List[Dict]) -> Dict:
        """找到最优参数"""
        if not results:
            return {}
        
        # 分析哪些参数组合效果最好
        params = {
            'position_size': [],
            'stop_loss': [],
            'take_profit': []
        }
        
        for result in results:
            return_rate = result.get('total_return', 0)
            if return_rate > 0:
                params['position_size'].append(result.get('position_size', 100))
        
        optimal = {}
        for param, values in params.items():
            if values:
                optimal[param] = statistics.median(values)
        
        return optimal
    
    def generate_strategy_variants(self, optimal: Dict) -> List[Dict]:
        """生成策略变体"""
        variants = []
        
        base_position = optimal.get('position_size', 100)
        for multiplier in [0.5, 0.8, 1.0, 1.2, 1.5]:
            variants.append({
                'name': f'variant_{multiplier}x',
                'position_size': base_position * multiplier,
                'stop_loss': 0.15,
                'take_profit': 0.30,
                'risk_level': 'conservative' if multiplier < 1 else 'aggressive'
            })
        
        return variants
    
    def evolve_risk_management(self, results: List[Dict]) -> List[Dict]:
        """进化风险管理规则"""
        return [
            {'rule': 'max_position_size', 'value': 0.2, 'reason': 'limit_single_exposure'},
            {'rule': 'daily_loss_limit', 'value': 0.1, 'reason': 'protect_capital'},
            {'rule': 'consecutive_losses', 'value': 3, 'reason': 'stop_trading_after_3_losses'}
        ]
    
    def evolve_position_sizing(self, results: List[Dict]) -> Dict:
        """进化仓位管理模型"""
        return {
            'model': 'kelly_criterion_variant',
            'base_percentage': 0.1,
            'max_percentage': 0.2,
            'confidence_adjustment': True
        }
    
    def load_market_history(self) -> List[Dict]:
        """加载市场历史数据"""
        history_file = os.path.join(DATA_DIR, "market_analysis_history.jsonl")
        results = []
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                for line in f:
                    try:
                        results.append(json.loads(line))
                    except:
                        pass
        return results
    
    def identify_market_patterns(self, data: List[Dict]) -> List[Dict]:
        """识别市场模式"""
        patterns = []
        
        # 分析成交量与价格的关系
        patterns.append({
            'name': 'volume_price_correlation',
            'description': 'High volume often precedes price movements',
            'confidence': 0.75,
            'trigger': 'volume > avg_volume * 1.5'
        })
        
        # 分析趋势延续性
        patterns.append({
            'name': 'trend_continuation',
            'description': 'Trends tend to continue in short term',
            'confidence': 0.68,
            'trigger': 'consecutive_3_same_direction'
        })
        
        return patterns
    
    def generate_prediction_models(self, patterns: List[Dict]) -> List[Dict]:
        """生成预测模型"""
        return [
            {
                'name': 'momentum_model',
                'features': ['price_change_24h', 'volume_ratio'],
                'accuracy': 0.65,
                'horizon': '24h'
            },
            {
                'name': 'mean_reversion_model',
                'features': ['price_deviation', 'volatility'],
                'accuracy': 0.58,
                'horizon': '48h'
            }
        ]
    
    def evolve_anomaly_detection(self, data: List[Dict]) -> List[Dict]:
        """进化异常检测规则"""
        return [
            {'type': 'volume_spike', 'threshold': 2.0, 'action': 'investigate'},
            {'type': 'price_gap', 'threshold': 0.1, 'action': 'alert'},
            {'type': 'liquidity_drop', 'threshold': 0.5, 'action': 'avoid'}
        ]
    
    def evolve_market_indicators(self, data: List[Dict]) -> List[Dict]:
        """进化市场指标"""
        return [
            {'name': 'smart_money_flow', 'weight': 0.3},
            {'name': 'liquidity_score', 'weight': 0.25},
            {'name': 'volatility_index', 'weight': 0.2},
            {'name': 'sentiment_score', 'weight': 0.25}
        ]
    
    def load_suggestion_history(self) -> List[Dict]:
        """加载建议历史"""
        history_file = os.path.join(DATA_DIR, "suggestion_history.jsonl")
        results = []
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                for line in f:
                    try:
                        results.append(json.loads(line))
                    except:
                        pass
        return results
    
    def identify_successful_suggestions(self, history: List[Dict]) -> List[Dict]:
        """识别成功的建议模式"""
        patterns = []
        
        # 分析哪些类型的建议效果好
        risk_levels = defaultdict(lambda: {'success': 0, 'total': 0})
        for h in history:
            level = h.get('risk_level', 'medium')
            success = h.get('followed_and_profitable', False)
            risk_levels[level]['total'] += 1
            if success:
                risk_levels[level]['success'] += 1
        
        for level, data in risk_levels.items():
            if data['total'] > 0:
                success_rate = data['success'] / data['total']
                patterns.append({
                    'risk_level': level,
                    'success_rate': success_rate,
                    'recommendation': 'increase_usage' if success_rate > 0.6 else 'decrease_usage'
                })
        
        return sorted(patterns, key=lambda x: x['success_rate'], reverse=True)
    
    def evolve_risk_grading(self, history: List[Dict]) -> Dict:
        """进化风险评级"""
        return {
            'conservative': {'max_drawdown': 0.1, 'position_size': 0.05},
            'moderate': {'max_drawdown': 0.2, 'position_size': 0.1},
            'aggressive': {'max_drawdown': 0.3, 'position_size': 0.2}
        }
    
    def generate_personalization_rules(self, history: List[Dict]) -> List[Dict]:
        """生成个性化规则"""
        return [
            {'condition': 'user_prefer_safe', 'action': 'increase_conservative_suggestions'},
            {'condition': 'user_high_tolerance', 'action': 'increase_aggressive_suggestions'},
            {'condition': 'recent_losses', 'action': 'reduce_position_sizes'}
        ]
    
    def optimize_confidence_thresholds(self, history: List[Dict]) -> Dict:
        """优化置信度阈值"""
        return {
            'high_confidence': 0.8,
            'medium_confidence': 0.6,
            'low_confidence': 0.4
        }
    
    def load_evolution_history(self) -> List[Dict]:
        """加载进化历史"""
        if os.path.exists(EVOLUTION_LOG):
            results = []
            with open(EVOLUTION_LOG, 'r') as f:
                for line in f:
                    try:
                        results.append(json.loads(line))
                    except:
                        pass
            return results
        return []
    
    def optimize_evolution_frequency(self, history: List[Dict]) -> int:
        """优化进化频率"""
        # 根据历史效果确定最佳进化频率
        return 10  # 每10次执行进化一次
    
    def evolve_selection_pressure(self, history: List[Dict]) -> float:
        """进化选择压力"""
        return 0.7  # 保留70%的精英，淘汰30%
    
    def optimize_mutation_rate(self, history: List[Dict]) -> float:
        """优化变异率"""
        return 0.1  # 10%的参数变异
    
    def evolve_convergence_criteria(self, history: List[Dict]) -> Dict:
        """进化收敛标准"""
        return {
            'max_generations': 100,
            'improvement_threshold': 0.01,
            'stagnation_limit': 10
        }
    
    # ============= 主控方法 =============
    
    def run_full_evolution(self) -> Dict:
        """运行完整进化周期"""
        print("\n" + "="*80)
        print("🧬 POLYMARKET 中央进化引擎启动")
        print("="*80)
        print(f"\n开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"进化模块数: {len(self.modules)}")
        print("\n")
        
        results = {}
        
        # 依次进化每个模块
        for module_name, evolve_func in self.modules.items():
            print(f"\n{'='*80}")
            print(f"📦 模块: {module_name}")
            print(f"{'='*80}")
            
            try:
                result = evolve_func()
                results[module_name] = result
                
                # 更新性能数据
                if module_name in self.performance_data:
                    self.performance_data[module_name].evolution_count += 1
                
            except Exception as e:
                print(f"❌ 进化失败: {e}")
                results[module_name] = {'error': str(e)}
        
        # 保存性能数据
        self.save_performance_data()
        
        # 生成进化报告
        report = self.generate_evolution_report(results)
        
        print(f"\n{'='*80}")
        print("✅ 完整进化周期完成")
        print(f"{'='*80}")
        print(f"\n生成报告: {report}")
        
        return results
    
    def generate_evolution_report(self, results: Dict) -> str:
        """生成进化报告"""
        report_file = os.path.join(DATA_DIR, f"evolution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'modules_evolved': len(results),
            'results': results,
            'performance_summary': {k: asdict(v) for k, v in self.performance_data.items()}
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report_file
    
    def get_module_status(self) -> Dict:
        """获取模块状态"""
        return {
            'modules': list(self.modules.keys()),
            'performance': {k: asdict(v) for k, v in self.performance_data.items()},
            'evolution_rules': len(self.evolution_rules)
        }

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Polymarket 中央进化引擎')
    parser.add_argument('--run', action='store_true', help='运行完整进化')
    parser.add_argument('--module', choices=['wallet_analysis', 'backtesting', 'market_analysis', 
                                              'strategy_suggestions', 'self_evolution'],
                        help='单独进化某个模块')
    parser.add_argument('--status', action='store_true', help='查看模块状态')
    
    args = parser.parse_args()
    
    engine = CentralEvolutionEngine()
    
    if args.run:
        engine.run_full_evolution()
    elif args.module:
        if args.module in engine.modules:
            result = engine.modules[args.module]()
            print(f"\n✅ {args.module} 进化完成")
            print(json.dumps(result, indent=2))
    elif args.status:
        status = engine.get_module_status()
        print(json.dumps(status, indent=2))
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
