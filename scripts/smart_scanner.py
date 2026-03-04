#!/usr/bin/env python3
"""
Polymarket 智能扫描与进化系统
集成钱包扫描、信号检测、自动学习和原则进化
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime, timedelta
from typing import List, Dict

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wallet_analysis import PolymarketWalletAnalyzer
from auto_evolution import AutoEvolutionSystem, TradingPrinciple

class SmartScanner:
    """智能扫描器 - 集成学习和进化"""
    
    def __init__(self):
        self.wallet_analyzer = PolymarketWalletAnalyzer()
        self.evolution_system = AutoEvolutionSystem()
        self.scan_history_file = os.path.expanduser(
            "~/.openclaw/workspace/.agents/skills/polymarket-analytics/data/scan_history.json"
        )
        self.load_scan_history()
    
    def load_scan_history(self):
        """加载扫描历史"""
        if os.path.exists(self.scan_history_file):
            with open(self.scan_history_file, 'r') as f:
                self.scan_history = json.load(f)
        else:
            self.scan_history = {'scanned_wallets': [], 'discovered_patterns': []}
    
    def save_scan_history(self):
        """保存扫描历史"""
        os.makedirs(os.path.dirname(self.scan_history_file), exist_ok=True)
        with open(self.scan_history_file, 'w') as f:
            json.dump(self.scan_history, f, indent=2)
    
    def smart_scan_wallet(self, address: str, learn: bool = True) -> Dict:
        """
        智能扫描钱包
        1. 分析钱包表现
        2. 自动学习模式
        3. 生成交易原则
        4. 更新进化系统
        """
        print(f"🚀 智能扫描: {address}")
        print("=" * 60)
        
        # 1. 基础分析
        print("\n📊 步骤1: 基础分析...")
        analysis_result = self.wallet_analyzer.analyze_wallet(address, days=90)
        
        if not analysis_result:
            print("❌ 钱包分析失败")
            return {}
        
        # 打印分析结果
        summary = analysis_result.get('summary', {})
        print(f"✅ 分析完成")
        print(f"   胜率: {summary.get('win_rate', 0)}%")
        print(f"   总盈亏: ${analysis_result.get('pnl', {}).get('total', 0):,.2f}")
        print(f"   夏普比率: {summary.get('sharpe_ratio', 0)}")
        
        # 2. 自动学习（如果启用）
        learning_result = None
        if learn:
            print("\n🧠 步骤2: 自动学习模式...")
            learning_result = self.evolution_system.analyze_wallet_pattern(address)
            
            if learning_result:
                print(f"✅ 学习完成")
                print(f"   生成 {learning_result['principles_generated']} 个新原则")
                
                # 记录到扫描历史
                self.scan_history['scanned_wallets'].append({
                    'address': address,
                    'scanned_at': datetime.now().isoformat(),
                    'win_rate': summary.get('win_rate', 0),
                    'principles_generated': learning_result['principles_generated']
                })
                self.save_scan_history()
        
        # 3. 基于当前原则生成信号建议
        print("\n📡 步骤3: 生成交易建议...")
        recommendations = self.generate_recommendations(analysis_result)
        
        for rec in recommendations:
            print(f"   💡 {rec}")
        
        # 4. 触发原则进化（如果扫描了足够多的钱包）
        if len(self.scan_history['scanned_wallets']) % 5 == 0:  # 每5个钱包触发一次进化
            print("\n🧬 步骤4: 触发原则进化...")
            evolve_result = self.evolution_system.evolve_principles()
            print(f"✅ 进化完成: +{evolve_result['new']} 新原则")
        
        return {
            'analysis': analysis_result,
            'learning': learning_result,
            'recommendations': recommendations
        }
    
    def generate_recommendations(self, analysis: Dict) -> List[str]:
        """基于分析生成交易建议"""
        recommendations = []
        
        summary = analysis.get('summary', {})
        pnl = analysis.get('pnl', {})
        
        win_rate = summary.get('win_rate', 0)
        sharpe = summary.get('sharpe_ratio', 0)
        total_pnl = pnl.get('total', 0)
        max_drawdown = summary.get('max_drawdown', 0)
        
        # 基于指标生成建议
        if win_rate > 60 and sharpe > 1.0 and total_pnl > 1000:
            recommendations.append(
                f"🟢 优质信号源: 胜率高({win_rate}%)，可跟随学习"
            )
        
        if sharpe > 1.5:
            recommendations.append(
                f"🟢 风险控制好: 夏普比率优秀({sharpe})"
            )
        elif sharpe < 0.5:
            recommendations.append(
                f"🟡 风险较高: 夏普比率偏低({sharpe})，谨慎参考"
            )
        
        if max_drawdown > 30:
            recommendations.append(
                f"🔴 回撤较大: 最大回撤{max_drawdown}%，注意风险控制"
            )
        elif max_drawdown < 15:
            recommendations.append(
                f"🟢 回撤控制佳: 最大回撤仅{max_drawdown}%"
            )
        
        if total_pnl > 10000:
            recommendations.append(
                f"🟢 盈利能力强: 总收益${total_pnl:,.2f}"
            )
        
        # 基于最佳原则生成建议
        best_principles = self.evolution_system.get_best_principles(3)
        if best_principles:
            recommendations.append(f"\n📚 当前最佳策略:")
            for p in best_principles[:2]:
                recommendations.append(f"   • {p.name} (准确度{p.accuracy:.0f}%)")
        
        if not recommendations:
            recommendations.append("⚪ 暂无明确建议，建议继续观察")
        
        return recommendations
    
    def batch_scan_wallets(self, addresses: List[str]) -> Dict:
        """批量扫描钱包并学习"""
        print(f"🚀 批量扫描 {len(addresses)} 个钱包\n")
        
        results = []
        smart_wallets = []
        
        for i, addr in enumerate(addresses, 1):
            print(f"\n[{i}/{len(addresses)}] 扫描钱包...")
            result = self.smart_scan_wallet(addr, learn=True)
            
            if result and result.get('analysis'):
                results.append(result)
                
                # 识别聪明钱
                summary = result['analysis'].get('summary', {})
                if summary.get('win_rate', 0) > 55 and summary.get('sharpe_ratio', 0) > 1.0:
                    smart_wallets.append({
                        'address': addr,
                        'win_rate': summary['win_rate'],
                        'sharpe': summary['sharpe_ratio']
                    })
            
            time.sleep(1)  # 避免请求过快
        
        # 总结
        print("\n" + "=" * 60)
        print("📊 批量扫描完成")
        print(f"   扫描钱包: {len(results)}")
        print(f"   识别聪明钱: {len(smart_wallets)}")
        
        if smart_wallets:
            print(f"\n🏆 推荐关注的聪明钱:")
            for w in sorted(smart_wallets, key=lambda x: x['win_rate'], reverse=True)[:5]:
                print(f"   • {w['address'][:20]}... 胜率{w['win_rate']:.1f}% 夏普{w['sharpe']:.2f}")
        
        # 触发最终进化
        print(f"\n🧬 触发原则进化...")
        evolve_result = self.evolution_system.evolve_principles()
        
        return {
            'scanned': len(results),
            'smart_wallets': smart_wallets,
            'evolution': evolve_result
        }
    
    def continuous_monitoring(self, wallets: List[str], interval_minutes: int = 60):
        """持续监控模式"""
        print(f"🔄 启动持续监控模式")
        print(f"   监控钱包: {len(wallets)} 个")
        print(f"   检查间隔: {interval_minutes} 分钟")
        print(f"   按 Ctrl+C 停止\n")
        
        try:
            while True:
                print(f"\n{'='*60}")
                print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 开始新一轮扫描")
                print('='*60)
                
                # 批量扫描
                result = self.batch_scan_wallets(wallets)
                
                # 验证信号
                print(f"\n🔍 验证历史信号...")
                validated = self.evolution_system.validate_signals()
                
                # 等待下一次
                print(f"\n⏳ 等待 {interval_minutes} 分钟后下次扫描...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 监控已停止")
            print("📚 最终原则库状态:")
            self.evolution_system.print_principles()

def main():
    parser = argparse.ArgumentParser(
        description='Polymarket 智能扫描与自动进化系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 扫描单个钱包并学习
  python3 smart_scanner.py -w 0x56687bf447db6ffa42ffe2204a05edaa20f55839
  
  # 批量扫描
  python3 smart_scanner.py -b 0xaddr1 0xaddr2 0xaddr3
  
  # 持续监控模式
  python3 smart_scanner.py -m 0xaddr1 0xaddr2 --interval 30
  
  # 只分析不学习
  python3 smart_scanner.py -w 0xaddr --no-learn
        """
    )
    
    parser.add_argument('--wallet', '-w', help='扫描单个钱包')
    parser.add_argument('--batch', '-b', nargs='+', help='批量扫描多个钱包')
    parser.add_argument('--monitor', '-m', nargs='+', help='持续监控钱包列表')
    parser.add_argument('--interval', '-i', type=int, default=60, help='监控间隔(分钟)')
    parser.add_argument('--no-learn', action='store_true', help='禁用自动学习')
    parser.add_argument('--principles', '-p', action='store_true', help='显示当前原则库')
    
    args = parser.parse_args()
    
    scanner = SmartScanner()
    
    if args.principles:
        scanner.evolution_system.print_principles()
    
    elif args.wallet:
        result = scanner.smart_scan_wallet(args.wallet, learn=not args.no_learn)
        
        if result and result.get('analysis'):
            # 输出格式化结果
            print("\n" + "="*60)
            print("📊 完整分析报告")
            print("="*60)
            
            analysis = result['analysis']
            summary = analysis.get('summary', {})
            pnl = analysis.get('pnl', {})
            
            print(f"\n基本指标:")
            print(f"   胜率: {summary.get('win_rate', 0)}%")
            print(f"   夏普比率: {summary.get('sharpe_ratio', 0)}")
            print(f"   最大回撤: {summary.get('max_drawdown', 0)}%")
            print(f"   总盈亏: ${pnl.get('total', 0):,.2f}")
            
            print(f"\n交易建议:")
            for rec in result.get('recommendations', []):
                print(f"   {rec}")
    
    elif args.batch:
        scanner.batch_scan_wallets(args.batch)
    
    elif args.monitor:
        scanner.continuous_monitoring(args.monitor, args.interval)
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
