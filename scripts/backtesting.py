#!/usr/bin/env python3
"""
Polymarket 模拟回测工具
功能：模拟跟随指定钱包的历史表现
"""

import argparse
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List
import statistics

DATA_API_URL = "https://data-api.polymarket.com"

class PolymarketBacktester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})
    
    def get_wallet_trades(self, address: str, start_time: int, end_time: int) -> List[Dict]:
        """获取钱包指定时间段的交易"""
        trades = []
        offset = 0
        
        while True:
            try:
                resp = self.session.get(
                    f"{DATA_API_URL}/trades",
                    params={
                        'user': address,
                        'startTime': start_time,
                        'endTime': end_time,
                        'limit': 500,
                        'offset': offset
                    },
                    timeout=30
                )
                resp.raise_for_status()
                data = resp.json()
                
                if not data:
                    break
                
                trades.extend(data)
                
                if len(data) < 500:
                    break
                
                offset += 500
                
            except Exception as e:
                print(f"❌ 获取交易失败: {e}")
                break
        
        return sorted(trades, key=lambda x: x.get('timestamp', 0))
    
    def simulate_copy_trading(self, target_trades: List[Dict], 
                              initial_capital: float = 1000,
                              position_size: float = 100,
                              fee_rate: float = 0.02) -> Dict:
        """模拟跟单交易"""
        
        if not target_trades:
            return {}
        
        capital = initial_capital
        positions = {}  # 当前持仓
        trades_history = []
        equity_curve = [capital]
        
        for trade in target_trades:
            # 简化模型：假设我们按比例跟随目标钱包的交易
            trade_type = trade.get('type', '')  # BUY or SELL
            amount = trade.get('size', 0)
            price = trade.get('price', 0)
            market_id = trade.get('marketId', '')
            timestamp = trade.get('timestamp', 0)
            
            # 计算我们的跟单规模
            our_size = min(position_size, capital * 0.1)  # 单仓位不超过10%
            
            if our_size <= 0:
                continue
            
            # 计算费用
            fee = our_size * fee_rate
            
            if trade_type == 'BUY':
                # 开仓
                if capital >= our_size + fee:
                    positions[market_id] = {
                        'entry_price': price,
                        'size': our_size,
                        'timestamp': timestamp
                    }
                    capital -= (our_size + fee)
                    
                    trades_history.append({
                        'type': 'BUY',
                        'market': market_id,
                        'price': price,
                        'size': our_size,
                        'fee': fee,
                        'timestamp': timestamp,
                        'capital_after': capital
                    })
            
            elif trade_type == 'SELL' and market_id in positions:
                # 平仓
                pos = positions[market_id]
                entry_price = pos['entry_price']
                position_size_actual = pos['size']
                
                # 计算盈亏
                if price > 0 and entry_price > 0:
                    pnl = position_size_actual * (price - entry_price) / entry_price
                else:
                    pnl = 0
                
                capital += position_size_actual + pnl - fee
                
                trades_history.append({
                    'type': 'SELL',
                    'market': market_id,
                    'entry_price': entry_price,
                    'exit_price': price,
                    'size': position_size_actual,
                    'pnl': pnl,
                    'fee': fee,
                    'timestamp': timestamp,
                    'capital_after': capital
                })
                
                del positions[market_id]
            
            equity_curve.append(capital)
        
        # 计算回测指标
        total_return = ((capital - initial_capital) / initial_capital) * 100
        
        profitable_trades = len([t for t in trades_history if t.get('pnl', 0) > 0])
        total_closed_trades = len([t for t in trades_history if t['type'] == 'SELL'])
        win_rate = (profitable_trades / total_closed_trades * 100) if total_closed_trades > 0 else 0
        
        # 计算最大回撤
        max_drawdown = self.calculate_max_drawdown(equity_curve)
        
        # 计算夏普比率
        returns = []
        for i in range(1, len(equity_curve)):
            if equity_curve[i-1] > 0:
                ret = (equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1]
                returns.append(ret)
        
        sharpe = self.calculate_sharpe(returns) if len(returns) > 1 else 0
        
        return {
            'initial_capital': initial_capital,
            'final_capital': round(capital, 2),
            'total_return': round(total_return, 2),
            'total_trades': len(trades_history),
            'closed_trades': total_closed_trades,
            'win_rate': round(win_rate, 2),
            'max_drawdown': round(max_drawdown, 2),
            'sharpe_ratio': round(sharpe, 2),
            'total_fees': round(sum(t.get('fee', 0) for t in trades_history), 2),
            'equity_curve': equity_curve,
            'trades': trades_history[-20:]  # 最近20笔
        }
    
    def calculate_max_drawdown(self, equity_curve: List[float]) -> float:
        """计算最大回撤"""
        if not equity_curve:
            return 0.0
        
        peak = equity_curve[0]
        max_dd = 0.0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            if peak > 0:
                dd = (peak - value) / peak
                max_dd = max(max_dd, dd)
        
        return max_dd * 100
    
    def calculate_sharpe(self, returns: List[float], risk_free: float = 0.02/365) -> float:
        """计算夏普比率"""
        if len(returns) < 2:
            return 0.0
        
        avg_return = statistics.mean(returns)
        std_dev = statistics.stdev(returns) if len(returns) > 1 else 0
        
        if std_dev == 0:
            return 0.0
        
        return (avg_return - risk_free) / std_dev
    
    def run_backtest(self, target_address: str, days: int, 
                     investment: float, position_size: float) -> Dict:
        """运行回测"""
        
        print(f"🔄 开始回测")
        print(f"👤 目标钱包: {target_address}")
        print(f"📅 回测周期: {days}天")
        print(f"💰 初始资金: ${investment:,.2f}")
        print(f"📊 单仓规模: ${position_size:,.2f}")
        print()
        
        # 计算时间范围
        end_time = int(datetime.now().timestamp())
        start_time = int((datetime.now() - timedelta(days=days)).timestamp())
        
        # 获取目标钱包交易
        print("📥 获取目标钱包交易数据...")
        target_trades = self.get_wallet_trades(target_address, start_time, end_time)
        
        if not target_trades:
            print("❌ 未找到目标钱包的交易数据")
            return {}
        
        print(f"✅ 获取到 {len(target_trades)} 笔交易")
        print()
        
        # 运行模拟
        print("🧮 运行模拟...")
        result = self.simulate_copy_trading(
            target_trades,
            initial_capital=investment,
            position_size=position_size
        )
        
        return result
    
    def format_output(self, result: Dict, format_type: str = 'text') -> str:
        """格式化输出"""
        if not result:
            return "❌ 回测失败"
        
        if format_type == 'telegram':
            output = f"📊 <b>Polymarket 回测报告</b>\n\n"
            output += f"💰 初始资金: <b>${result['initial_capital']:,.2f}</b>\n"
            output += f"💵 最终资金: <b>${result['final_capital']:,.2f}</b>\n"
            output += f"📈 总收益率: <b>{result['total_return']}%</b>\n\n"
            
            output += f"📊 <b>交易统计</b>\n"
            output += f"• 总交易: {result['total_trades']}\n"
            output += f"• 已平仓: {result['closed_trades']}\n"
            output += f"• 胜率: <b>{result['win_rate']}%</b>\n"
            output += f"• 夏普比率: {result['sharpe_ratio']}\n"
            output += f"• 最大回撤: <b>{result['max_drawdown']}%</b>\n"
            output += f"• 总手续费: ${result['total_fees']:,.2f}\n"
        else:
            output = f"📊 Polymarket 回测报告\n"
            output += f"{'='*50}\n\n"
            output += f"💰 初始资金: ${result['initial_capital']:,.2f}\n"
            output += f"💵 最终资金: ${result['final_capital']:,.2f}\n"
            output += f"📈 总收益率: {result['total_return']}%\n"
            output += f"💵 绝对收益: ${result['final_capital'] - result['initial_capital']:,.2f}\n\n"
            
            output += "📊 交易统计\n"
            output += f"  总交易: {result['total_trades']}\n"
            output += f"  已平仓: {result['closed_trades']}\n"
            output += f"  胜率: {result['win_rate']}%\n"
            output += f"  夏普比率: {result['sharpe_ratio']}\n"
            output += f"  最大回撤: {result['max_drawdown']}%\n"
            output += f"  总手续费: ${result['total_fees']:,.2f}\n\n"
            
            if result['trades']:
                output += "📝 最近交易:\n"
                for trade in result['trades'][-5:]:
                    pnl = trade.get('pnl', 0)
                    pnl_emoji = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
                    output += f"  {pnl_emoji} {trade['type']} - PnL: ${pnl:,.2f}\n"
        
        return output

def main():
    parser = argparse.ArgumentParser(description='Polymarket 回测工具')
    parser.add_argument('--target', '-t', required=True, help='目标钱包地址')
    parser.add_argument('--days', '-d', type=int, default=90, help='回测天数')
    parser.add_argument('--investment', '-i', type=float, default=1000, help='初始资金')
    parser.add_argument('--position-size', '-p', type=float, default=100, help='单仓规模')
    parser.add_argument('--fee-rate', '-f', type=float, default=0.02, help='手续费率')
    parser.add_argument('--output-format', choices=['text', 'telegram', 'json'], 
                        default='text')
    parser.add_argument('--output', '-o', help='输出文件')
    
    args = parser.parse_args()
    
    backtester = PolymarketBacktester()
    result = backtester.run_backtest(
        args.target, 
        args.days, 
        args.investment,
        args.position_size
    )
    
    if not result:
        print("❌ 回测失败")
        return
    
    if args.output_format == 'json':
        output = json.dumps(result, indent=2)
    else:
        output = backtester.format_output(result, args.output_format)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"✅ 结果已保存: {args.output}")
    else:
        print(output)

if __name__ == '__main__':
    main()
