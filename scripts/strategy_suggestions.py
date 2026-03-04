#!/usr/bin/env python3
"""
Polymarket 策略建议工具
功能：基于数据分析生成交易策略建议
"""

import argparse
import json
import requests
from datetime import datetime
from typing import Dict, List

DATA_API_URL = "https://data-api.polymarket.com"
GAMMA_API_URL = "https://gamma-api.polymarket.com"

class PolymarketStrategyAdvisor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})
        
        # 风险配置
        self.risk_configs = {
            'conservative': {
                'max_position_size': 0.05,  # 单仓不超过5%
                'min_liquidity': 50000,
                'stop_loss': 0.15,
                'take_profit': 0.30,
                'description': '保守型 - 低风险，稳定收益'
            },
            'moderate': {
                'max_position_size': 0.10,  # 单仓不超过10%
                'min_liquidity': 20000,
                'stop_loss': 0.20,
                'take_profit': 0.50,
                'description': '稳健型 - 平衡风险与收益'
            },
            'aggressive': {
                'max_position_size': 0.20,  # 单仓不超过20%
                'min_liquidity': 5000,
                'stop_loss': 0.30,
                'take_profit': 1.00,
                'description': '激进型 - 高风险，高潜在收益'
            }
        }
    
    def get_leaderboard(self, limit: int = 20) -> List[Dict]:
        """获取交易排行榜"""
        try:
            resp = self.session.get(
                f"{DATA_API_URL}/leaderboard",
                params={'limit': limit},
                timeout=30
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"❌ 获取排行榜失败: {e}")
            return []
    
    def analyze_wallet(self, address: str) -> Dict:
        """分析钱包并生成建议"""
        try:
            # 获取持仓
            resp = self.session.get(
                f"{DATA_API_URL}/positions",
                params={'user': address, 'limit': 100},
                timeout=30
            )
            resp.raise_for_status()
            positions = resp.json()
            
            # 获取活动
            resp = self.session.get(
                f"{DATA_API_URL}/activity",
                params={'user': address},
                timeout=30
            )
            resp.raise_for_status()
            activity = resp.json()
            
            return {'positions': positions, 'activity': activity}
        except Exception as e:
            print(f"❌ 分析钱包失败: {e}")
            return {}
    
    def identify_smart_money(self) -> List[Dict]:
        """识别聪明钱"""
        leaderboard = self.get_leaderboard(50)
        
        smart_wallets = []
        for trader in leaderboard:
            # 筛选标准：高胜率 + 正收益
            win_rate = trader.get('winRate', 0)
            pnl = trader.get('pnl', 0)
            volume = trader.get('volume', 0)
            
            if win_rate > 55 and pnl > 10000 and volume > 100000:
                smart_wallets.append({
                    'address': trader.get('address'),
                    'win_rate': win_rate,
                    'pnl': pnl,
                    'volume': volume,
                    'trades': trader.get('trades', 0)
                })
        
        return sorted(smart_wallets, key=lambda x: x['pnl'], reverse=True)[:10]
    
    def generate_strategy(self, risk_level: str = 'moderate') -> Dict:
        """生成策略建议"""
        config = self.risk_configs.get(risk_level, self.risk_configs['moderate'])
        
        # 识别聪明钱
        print("🔍 识别聪明钱钱包...")
        smart_money = self.identify_smart_money()
        
        # 生成策略框架
        strategy = {
            'risk_level': risk_level,
            'config': config,
            'smart_money_targets': smart_money[:5],
            'rules': {
                'position_sizing': {
                    'max_per_position': f"{config['max_position_size']*100}%",
                    'description': f"单笔投资不超过总资金的{config['max_position_size']*100}%"
                },
                'market_selection': {
                    'min_liquidity': f"${config['min_liquidity']:,}",
                    'description': f"只选择流动性大于${config['min_liquidity']:,}的市场"
                },
                'risk_management': {
                    'stop_loss': f"{config['stop_loss']*100}%",
                    'take_profit': f"{config['take_profit']*100}%",
                    'description': f"止损线{config['stop_loss']*100}%，止盈线{config['take_profit']*100}%"
                },
                'entry_criteria': [
                    '选择近期有趋势的市场',
                    '关注聪明钱的动向',
                    '分析市场情绪指标',
                    '确保充足的流动性'
                ],
                'exit_criteria': [
                    '触及止损线立即退出',
                    '达到止盈目标分批退出',
                    '市场趋势反转信号',
                    '临近结算日提前退出'
                ]
            },
            'recommended_allocation': {
                'high_confidence': f"{config['max_position_size']*100}%",
                'medium_confidence': f"{config['max_position_size']*0.6*100}%",
                'low_confidence': f"{config['max_position_size']*0.3*100}%"
            }
        }
        
        return strategy
    
    def format_output(self, strategy: Dict, format_type: str = 'text') -> str:
        """格式化输出"""
        if not strategy:
            return "❌ 生成策略失败"
        
        config = strategy.get('config', {})
        rules = strategy.get('rules', {})
        
        if format_type == 'telegram':
            output = f"🎯 <b>Polymarket 策略建议</b>\n\n"
            output += f"📊 风险等级: <b>{config.get('description', '')}</b>\n\n"
            
            # 聪明钱目标
            output += "💡 <b>建议关注的聪明钱</b>\n"
            for i, wallet in enumerate(strategy.get('smart_money_targets', [])[:3], 1):
                output += f"{i}. <code>{wallet['address'][:15]}...</code>\n"
                output += f"   胜率: {wallet['win_rate']}% | PnL: ${wallet['pnl']:,.0f}\n\n"
            
            # 策略规则
            output += "📋 <b>策略规则</b>\n"
            output += f"• 仓位: {rules.get('position_sizing', {}).get('max_per_position', '10%')}\n"
            output += f"• 流动性: {rules.get('market_selection', {}).get('min_liquidity', '$20,000')}\n"
            output += f"• 止损: {rules.get('risk_management', {}).get('stop_loss', '20%')}\n"
            output += f"• 止盈: {rules.get('risk_management', {}).get('take_profit', '50%')}\n\n"
            
            output += "✅ <b>入场条件</b>\n"
            for criterion in rules.get('entry_criteria', []):
                output += f"• {criterion}\n"
            
            output += "\n🚪 <b>出场条件</b>\n"
            for criterion in rules.get('exit_criteria', []):
                output += f"• {criterion}\n"
        
        else:
            output = f"🎯 Polymarket 策略建议\n"
            output += f"{'='*50}\n\n"
            output += f"风险等级: {config.get('description', '')}\n\n"
            
            output += "💡 建议关注的聪明钱\n"
            for i, wallet in enumerate(strategy.get('smart_money_targets', []), 1):
                output += f"  {i}. 地址: {wallet['address']}\n"
                output += f"     胜率: {wallet['win_rate']}%\n"
                output += f"     累计收益: ${wallet['pnl']:,.2f}\n"
                output += f"     交易次数: {wallet['trades']}\n\n"
            
            output += "📋 策略规则\n"
            pos = rules.get('position_sizing', {})
            output += f"  仓位管理: {pos.get('description', '')}\n\n"
            
            market = rules.get('market_selection', {})
            output += f"  市场选择: {market.get('description', '')}\n\n"
            
            risk = rules.get('risk_management', {})
            output += f"  风险管理: {risk.get('description', '')}\n\n"
            
            output += "✅ 入场条件\n"
            for i, criterion in enumerate(rules.get('entry_criteria', []), 1):
                output += f"  {i}. {criterion}\n"
            
            output += "\n🚪 出场条件\n"
            for i, criterion in enumerate(rules.get('exit_criteria', []), 1):
                output += f"  {i}. {criterion}\n"
            
            alloc = strategy.get('recommended_allocation', {})
            output += "\n📊 建议仓位分配\n"
            output += f"  高信心: {alloc.get('high_confidence', '10%')}\n"
            output += f"  中信心: {alloc.get('medium_confidence', '6%')}\n"
            output += f"  低信心: {alloc.get('low_confidence', '3%')}\n"
        
        return output

def main():
    parser = argparse.ArgumentParser(description='Polymarket 策略建议工具')
    parser.add_argument('--risk-level', '-r', 
                        choices=['conservative', 'moderate', 'aggressive'],
                        default='moderate', help='风险等级')
    parser.add_argument('--output-format', '-f', 
                        choices=['text', 'telegram', 'json'],
                        default='text')
    parser.add_argument('--output', '-o', help='输出文件')
    
    args = parser.parse_args()
    
    print(f"🎯 正在生成 {args.risk_level} 策略...")
    print()
    
    advisor = PolymarketStrategyAdvisor()
    strategy = advisor.generate_strategy(args.risk_level)
    
    if not strategy:
        print("❌ 生成策略失败")
        return
    
    if args.output_format == 'json':
        output = json.dumps(strategy, indent=2)
    else:
        output = advisor.format_output(strategy, args.output_format)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"✅ 策略已保存: {args.output}")
    else:
        print(output)

if __name__ == '__main__':
    main()
