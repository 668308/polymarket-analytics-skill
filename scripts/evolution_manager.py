#!/usr/bin/env python3
"""
进化管理器 - 统一管理和调度所有模块的进化
"""

import os
import sys
import json
import time
import schedule
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from central_evolution_engine import CentralEvolutionEngine

class EvolutionManager:
    """进化管理器 - 统一管理所有模块的自动进化"""
    
    def __init__(self):
        self.engine = CentralEvolutionEngine()
        self.evolution_schedule = {
            'wallet_analysis': {'frequency': 10, 'counter': 0},  # 每10次执行
            'backtesting': {'frequency': 5, 'counter': 0},
            'market_analysis': {'frequency': 3, 'counter': 0},
            'strategy_suggestions': {'frequency': 7, 'counter': 0},
            'self_evolution': {'frequency': 15, 'counter': 0}  # 元进化
        }
        self.running = False
        
    def check_and_trigger_evolution(self, module_name: str):
        """检查并触发进化"""
        if module_name not in self.evolution_schedule:
            return
        
        schedule_config = self.evolution_schedule[module_name]
        schedule_config['counter'] += 1
        
        if schedule_config['counter'] >= schedule_config['frequency']:
            print(f"\n🧬 [{datetime.now().strftime('%H:%M:%S')}] 触发 {module_name} 模块进化")
            
            # 执行进化
            if module_name == 'wallet_analysis':
                self.engine.evolve_wallet_analysis()
            elif module_name == 'backtesting':
                self.engine.evolve_backtesting()
            elif module_name == 'market_analysis':
                self.engine.evolve_market_analysis()
            elif module_name == 'strategy_suggestions':
                self.engine.evolve_strategy_suggestions()
            elif module_name == 'self_evolution':
                self.engine.evolve_self_evolution()
            
            # 重置计数器
            schedule_config['counter'] = 0
            
            print(f"✅ {module_name} 进化完成\n")
    
    def run_periodic_evolution(self):
        """运行定期进化"""
        print("\n" + "="*80)
        print("🔄 POLYMARKET 自动进化系统启动")
        print("="*80)
        print(f"\n启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n进化计划:")
        for module, config in self.evolution_schedule.items():
            print(f"  • {module}: 每 {config['frequency']} 次执行")
        print("\n" + "="*80)
        print("\n按 Ctrl+C 停止\n")
        
        self.running = True
        
        try:
            while self.running:
                # 模拟各模块的执行和进化触发
                for module in self.evolution_schedule.keys():
                    # 这里实际应该调用各模块的功能
                    # 现在只是模拟计数
                    pass
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n🛑 自动进化系统已停止")
    
    def run_full_evolution_now(self):
        """立即运行完整进化"""
        print("\n🚀 手动触发完整进化...")
        results = self.engine.run_full_evolution()
        return results
    
    def get_evolution_status(self) -> Dict:
        """获取进化状态"""
        return {
            'schedule': self.evolution_schedule,
            'module_status': self.engine.get_module_status(),
            'next_evolutions': {
                module: config['frequency'] - config['counter']
                for module, config in self.evolution_schedule.items()
            }
        }
    
    def adjust_evolution_frequency(self, module: str, new_frequency: int):
        """调整进化频率"""
        if module in self.evolution_schedule:
            self.evolution_schedule[module]['frequency'] = new_frequency
            print(f"✅ {module} 进化频率已调整为: 每 {new_frequency} 次执行")
    
    def force_evolution(self, module: str):
        """强制触发某个模块的进化"""
        print(f"\n🚀 强制触发 {module} 进化...")
        
        if module == 'wallet_analysis':
            result = self.engine.evolve_wallet_analysis()
        elif module == 'backtesting':
            result = self.engine.evolve_backtesting()
        elif module == 'market_analysis':
            result = self.engine.evolve_market_analysis()
        elif module == 'strategy_suggestions':
            result = self.engine.evolve_strategy_suggestions()
        elif module == 'self_evolution':
            result = self.engine.evolve_self_evolution()
        else:
            print(f"❌ 未知模块: {module}")
            return None
        
        # 重置计数器
        if module in self.evolution_schedule:
            self.evolution_schedule[module]['counter'] = 0
        
        return result

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Polymarket 进化管理器')
    parser.add_argument('--run', action='store_true', help='运行自动进化系统')
    parser.add_argument('--evolve-now', action='store_true', help='立即运行完整进化')
    parser.add_argument('--force', help='强制进化指定模块')
    parser.add_argument('--status', action='store_true', help='查看进化状态')
    parser.add_argument('--adjust', nargs=2, metavar=('MODULE', 'FREQUENCY'),
                        help='调整进化频率 (例如: --adjust wallet_analysis 5)')
    
    args = parser.parse_args()
    
    manager = EvolutionManager()
    
    if args.run:
        manager.run_periodic_evolution()
    elif args.evolve_now:
        results = manager.run_full_evolution_now()
        print("\n进化结果:")
        print(json.dumps(results, indent=2))
    elif args.force:
        result = manager.force_evolution(args.force)
        if result:
            print(json.dumps(result, indent=2))
    elif args.status:
        status = manager.get_evolution_status()
        print(json.dumps(status, indent=2))
    elif args.adjust:
        module, freq = args.adjust
        manager.adjust_evolution_frequency(module, int(freq))
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
