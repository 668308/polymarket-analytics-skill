#!/usr/bin/env python3
"""
Polymarket 钱包分析工具
功能：分析指定钱包的交易表现、胜率、PnL、风险指标
"""

import argparse
import json
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import statistics

# API 配置
DATA_API_URL = "https://data-api.polymarket.com"
GAMMA_API_URL = "https://gamma-api.polymarket.com"

class PolymarketWalletAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def get_user_positions(self, address: str) -> List[Dict]:
        """获取用户当前持仓"""
        try:
            resp = self.session.get(
                f"{DATA_API_URL}/positions",
                params={
                    'user': address,
                    'limit': 500,
                    'sortBy': 'CASHPNL',
                    'sortDirection': 'DESC'
                },
                timeout=30
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"❌ 获取持仓失败: {e}")
            return []
    
    def get_user_trades(self, address: str, days: int = 90) -> List[Dict]:
        """获取用户交易历史"""
        try:
            # 计算开始时间戳
            start_time = int((datetime.now() - timedelta(days=days)).timestamp())
            
            resp = self.session.get(
                f"{DATA_API_URL}/trades",
                params={
                    'user': address,
                    'limit': 500,
                    'startTime': start_time
                },
                timeout=30
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"❌ 获取交易历史失败: {e}")
            return []
    
    def get_user_activity(self, address: str) -> Dict:
        """获取用户活动统计"""
        try:
            resp = self.session.get(
                f"{DATA_API_URL}/activity",
                params={'user': address},
                timeout=30
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"❌ 获取活动统计失败: {e}")
            return {}
    
    def calculate_win_rate(self, trades: List[Dict]) -> float:
        """计算胜率"""
        if not trades:
            return 0.0
        
        profitable_trades = 0
        for trade in trades:
            pnl = trade.get('realizedPnl', 0)
            if pnl > 0:
                profitable_trades += 1
        
        return (profitable_trades / len(trades)) * 100
    
    def calculate_pnl_stats(self, positions: List[Dict]) -> Dict:
        """计算盈亏统计"""
        total_realized_pnl = sum(p.get('realizedPnl', 0) for p in positions)
        total_unrealized_pnl = sum(p.get('unrealizedPnl', 0) for p in positions)
        
        # 已实现盈亏分布
        realized_pnls = [p.get('realizedPnl', 0) for p in positions if p.get('realizedPnl', 0) != 0]
        
        return {
            'total_realized_pnl': total_realized_pnl,
            'total_unrealized_pnl': total_unrealized_pnl,
            'total_pnl': total_realized_pnl + total_unrealized_pnl,
            'avg_realized_pnl': statistics.mean(realized_pnls) if realized_pnls else 0,
            'max_profit': max(realized_pnls) if realized_pnls else 0,
            'max_loss': min(realized_pnls) if realized_pnls else 0,
            'profitable_positions': len([p for p in realized_pnls if p > 0]),
            'losing_positions': len([p for p in realized_pnls if p < 0])
        }
    
    def calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 0.02) -> float:
        """计算夏普比率"""
        if len(returns) < 2:
            return 0.0
        
        avg_return = statistics.mean(returns)
        std_dev = statistics.stdev(returns) if len(returns) > 1 else 0
        
        if std_dev == 0:
            return 0.0
        
        return (avg_return - risk_free_rate) / std_dev
    
    def calculate_max_drawdown(self, equity_curve: List[float]) -> float:
        """计算最大回撤"""
        if not equity_curve:
            return 0.0
        
        peak = equity_curve[0]
        max_drawdown = 0.0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak if peak > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown * 100
    
    def analyze_wallet(self, address: str, days: int = 90) -> Dict:
        """完整的钱包分析"""
        print(f"🔍 正在分析钱包: {address}")
        print(f"⏱️  分析周期: 过去 {days} 天")
        print()
        
        # 获取数据
        positions = self.get_user_positions(address)
        trades = self.get_user_trades(address, days)
        activity = self.get_user_activity(address)
        
        if not positions and not trades:
            print("⚠️  未找到该钱包的交易数据")
            return {}
        
        # 计算指标
        pnl_stats = self.calculate_pnl_stats(positions)
        win_rate = self.calculate_win_rate(trades)
        
        # 构建权益曲线用于计算回撤
        equity_curve = []
        cumulative_pnl = 0
        for trade in sorted(trades, key=lambda x: x.get('timestamp', 0)):
            cumulative_pnl += trade.get('realizedPnl', 0)
            equity_curve.append(cumulative_pnl)
        
        max_drawdown = self.calculate_max_drawdown(equity_curve)
        
        # 计算夏普比率（按月收益率）
        monthly_returns = []
        for i in range(0, len(equity_curve), 30):
            if i + 30 < len(equity_curve):
                monthly_return = (equity_curve[i+30] - equity_curve[i]) / abs(equity_curve[i]) if equity_curve[i] != 0 else 0
                monthly_returns.append(monthly_return)
        
        sharpe_ratio = self.calculate_sharpe_ratio(monthly_returns)
        
        # 持仓分析
        active_positions = len([p for p in positions if p.get('tokens', 0) > 0])
        resolved_positions = len(positions) - active_positions
        
        result = {
            'address': address,
            'analysis_time': datetime.now().isoformat(),
            'period_days': days,
            'summary': {
                'total_positions': len(positions),
                'active_positions': active_positions,
                'resolved_positions': resolved_positions,
                'total_trades': len(trades),
                'win_rate': round(win_rate, 2),
                'sharpe_ratio': round(sharpe_ratio, 2),
                'max_drawdown': round(max_drawdown, 2)
            },
            'pnl': {
                'total_realized': round(pnl_stats['total_realized_pnl'], 2),
                'total_unrealized': round(pnl_stats['total_unrealized_pnl'], 2),
                'total': round(pnl_stats['total_pnl'], 2),
                'average_per_trade': round(pnl_stats['avg_realized_pnl'], 2),
                'max_profit': round(pnl_stats['max_profit'], 2),
                'max_loss': round(pnl_stats['max_loss'], 2)
            },
            'activity': activity,
            'top_positions': positions[:5] if positions else []
        }
        
        return result
    
    def format_output(self, result: Dict, format_type: str = 'text') -> str:
        """格式化输出"""
        if not result:
            return "⚠️  无数据"
        
        summary = result.get('summary', {})
        pnl = result.get('pnl', {})
        
        if format_type == 'telegram':
            output = f"📊 <b>Polymarket 钱包分析</b>\n\n"
            output += f"👤 地址: <code>{result['address'][:20]}...</code>\n"
            output += f"📅 分析周期: {result['period_days']}天\n\n"
            
            output += f"📈 <b>交易表现</b>\n"
            output += f"• 胜率: <b>{summary.get('win_rate', 0)}%</b>\n"
            output += f"• 夏普比率: <b>{summary.get('sharpe_ratio', 0)}</b>\n"
            output += f"• 最大回撤: <b>{summary.get('max_drawdown', 0)}%</b>\n\n"
            
            output += f"💰 <b>盈亏统计</b>\n"
            output += f"• 已实现盈亏: <b>${pnl.get('total_realized', 0):,.2f}</b>\n"
            output += f"• 未实现盈亏: <b>${pnl.get('total_unrealized', 0):,.2f}</b>\n"
            output += f"• 总盈亏: <b>${pnl.get('total', 0):,.2f}</b>\n\n"
            
            output += f"📊 <b>持仓概况</b>\n"
            output += f"• 总持仓: {summary.get('total_positions', 0)}\n"
            output += f"• 活跃持仓: {summary.get('active_positions', 0)}\n"
            output += f"• 总交易次数: {summary.get('total_trades', 0)}\n"
            
        else:
            output = f"📊 Polymarket 钱包分析报告\n"
            output += f"{'='*50}\n\n"
            output += f"地址: {result['address']}\n"
            output += f"分析周期: {result['period_days']}天\n"
            output += f"分析时间: {result['analysis_time']}\n\n"
            
            output += "📈 交易表现\n"
            output += f"  胜率: {summary.get('win_rate', 0)}%\n"
            output += f"  夏普比率: {summary.get('sharpe_ratio', 0)}\n"
            output += f"  最大回撤: {summary.get('max_drawdown', 0)}%\n\n"
            
            output += "💰 盈亏统计\n"
            output += f"  已实现盈亏: ${pnl.get('total_realized', 0):,.2f}\n"
            output += f"  未实现盈亏: ${pnl.get('total_unrealized', 0):,.2f}\n"
            output += f"  总盈亏: ${pnl.get('total', 0):,.2f}\n"
            output += f"  平均每笔: ${pnl.get('average_per_trade', 0):,.2f}\n"
            output += f"  最大盈利: ${pnl.get('max_profit', 0):,.2f}\n"
            output += f"  最大亏损: ${pnl.get('max_loss', 0):,.2f}\n\n"
            
            output += "📊 持仓概况\n"
            output += f"  总持仓: {summary.get('total_positions', 0)}\n"
            output += f"  活跃持仓: {summary.get('active_positions', 0)}\n"
            output += f"  已结算: {summary.get('resolved_positions', 0)}\n"
            output += f"  总交易: {summary.get('total_trades', 0)}\n"
        
        return output

def main():
    parser = argparse.ArgumentParser(description='Polymarket 钱包分析工具')
    parser.add_argument('--address', '-a', required=True, help='钱包地址 (0x...)')
    parser.add_argument('--days', '-d', type=int, default=90, help='分析天数 (默认90天)')
    parser.add_argument('--output-format', '-f', choices=['text', 'telegram', 'json'], 
                        default='text', help='输出格式')
    parser.add_argument('--output', '-o', help='输出文件路径')
    
    args = parser.parse_args()
    
    # 验证地址格式
    if not args.address.startswith('0x') or len(args.address) != 42:
        print("❌ 错误: 无效的钱包地址格式")
        return
    
    # 执行分析
    analyzer = PolymarketWalletAnalyzer()
    result = analyzer.analyze_wallet(args.address, args.days)
    
    if not result:
        print("❌ 分析失败")
        return
    
    # 输出结果
    if args.output_format == 'json':
        output = json.dumps(result, indent=2, ensure_ascii=False)
    else:
        output = analyzer.format_output(result, args.output_format)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"✅ 结果已保存到: {args.output}")
    else:
        print(output)

if __name__ == '__main__':
    main()
