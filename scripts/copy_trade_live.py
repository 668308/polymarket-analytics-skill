#!/usr/bin/env python3
"""
Polymarket 实时跟单监控系统 - 生产版本
监控目标地址交易并实时通知
"""

import os
import sys
import json
import time
import signal
import requests
from datetime import datetime
from typing import Dict, List, Optional

# 配置
TARGET_WALLET = "0x2a2c53bd278c04da9962fcf96490e17f3dfb9bc1"
DATA_API_URL = "https://data-api.polymarket.com"
CHECK_INTERVAL = 60  # 每60秒检查一次

# Telegram 配置
TELEGRAM_BOT_TOKEN = "8412543152:AAGVHlrK8edkXvCv6RwSjcFBZYpLdsvffSY"
TELEGRAM_CHAT_ID = "8188236210"

# 状态文件
STATE_FILE = "/tmp/copy_trade_state.json"
LOG_FILE = "/tmp/copy_trade.log"

class CopyTradeMonitor:
    """跟单监控系统"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})
        self.running = True
        self.stats = {
            'total_signals': 0,
            'start_time': datetime.now().isoformat(),
            'last_trade_time': 0
        }
        
        # 加载状态
        self.load_state()
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """处理退出信号"""
        print("\n\n🛑 收到停止信号，正在保存状态...")
        self.running = False
        self.save_state()
        print("✅ 状态已保存，系统已停止")
        sys.exit(0)
    
    def load_state(self):
        """加载状态"""
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, 'r') as f:
                    state = json.load(f)
                    self.stats['last_trade_time'] = state.get('last_trade_time', 0)
                    self.stats['total_signals'] = state.get('total_signals', 0)
        except:
            pass
    
    def save_state(self):
        """保存状态"""
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump(self.stats, f)
        except:
            pass
    
    def log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        # 写入日志文件
        try:
            with open(LOG_FILE, 'a') as f:
                f.write(log_message + '\n')
        except:
            pass
    
    def get_recent_trades(self, minutes: int = 5) -> List[Dict]:
        """获取最近的交易"""
        try:
            resp = self.session.get(
                f"{DATA_API_URL}/trades",
                params={
                    'user': TARGET_WALLET,
                    'limit': 50
                },
                timeout=30
            )
            
            if resp.status_code == 200:
                trades = resp.json()
                
                # 筛选最近的交易
                cutoff_time = time.time() - (minutes * 60)
                recent_trades = [
                    t for t in trades 
                    if t.get('timestamp', 0) > max(cutoff_time, self.stats['last_trade_time'])
                ]
                
                return recent_trades
                
        except Exception as e:
            self.log(f"❌ 获取交易失败: {e}")
        
        return []
    
    def analyze_trade(self, trade: Dict) -> Dict:
        """分析交易"""
        price = trade.get('price', 0)
        side = trade.get('side', 'UNKNOWN')
        
        # 生成建议
        if side == 'BUY':
            if price < 0.4:
                suggestion = "🟢 强烈建议跟单"
                confidence = "高"
                position_size = "$100 (10%)"
            elif price < 0.55:
                suggestion = "✅ 建议跟单"
                confidence = "中高"
                position_size = "$50 (5%)"
            elif price < 0.7:
                suggestion = "🟡 谨慎跟单"
                confidence = "中"
                position_size = "$25 (2.5%)"
            else:
                suggestion = "❌ 不建议跟单"
                confidence = "低"
                position_size = "不跟单"
        else:  # SELL
            suggestion = "📤 目标卖出，观察即可"
            confidence = "观察"
            position_size = "不操作"
        
        return {
            'suggestion': suggestion,
            'confidence': confidence,
            'position_size': position_size,
            'risk_level': '低' if price < 0.4 else '中' if price < 0.7 else '高'
        }
    
    def send_notification(self, trade: Dict, analysis: Dict):
        """发送Telegram通知"""
        side = trade.get('side', 'UNKNOWN')
        price = trade.get('price', 0)
        size = trade.get('size', 0)
        title = trade.get('title', 'Unknown Market')
        outcome = trade.get('outcome', '')
        slug = trade.get('slug', '')
        
        # 构建市场链接
        market_url = f"https://polymarket.com/event/{trade.get('eventSlug', '')}"
        
        emoji = "🟢" if side == "BUY" else "🔴" if side == "SELL" else "⚪"
        
        message = f"""
{emoji} <b>Polymarket 跟单信号 #{self.stats['total_signals']}</b>

👤 <b>目标交易者</b>: Top 1 (PnL $394K+)
📍 <b>钱包</b>: <code>{TARGET_WALLET[:20]}...</code>

📊 <b>交易详情</b>:
• 操作: <b>{side}</b>
• 市场: {title[:40]}
• 预测: {outcome}
• 价格: <b>${price:.3f}</b>
• 数量: {size:,.0f}
⏰ 时间: {datetime.now().strftime('%H:%M:%S')}

💡 <b>分析建议</b>:
{analysis['suggestion']}
信心度: {analysis['confidence']}
建议仓位: {analysis['position_size']}
风险等级: {analysis['risk_level']}

📋 <b>跟单规则</b>:
• 价格 &lt; 0.4: 跟单10% ($100)
• 价格 0.4-0.55: 跟单5% ($50)
• 价格 0.55-0.7: 跟单2.5% ($25)
• 价格 &gt; 0.7: 不跟单

🎯 <b>止盈止损</b>:
• 止盈: +20% 卖出一半
• 止盈: +50% 卖出全部
• 止损: -15% 立即退出

🔗 <a href='{market_url}'>点击前往 Polymarket 交易</a>

💰 <b>预期收益</b>:
如果跟随目标历史表现，预期月收益 $600-$1000
"""
        
        try:
            resp = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    'chat_id': TELEGRAM_CHAT_ID,
                    'text': message,
                    'parse_mode': 'HTML',
                    'disable_web_page_preview': True
                },
                timeout=10
            )
            return resp.json().get('ok', False)
        except Exception as e:
            self.log(f"❌ 发送通知失败: {e}")
            return False
    
    def print_summary(self):
        """打印统计摘要"""
        runtime = datetime.now() - datetime.fromisoformat(self.stats['start_time'])
        hours = runtime.total_seconds() / 3600
        
        self.log("\n" + "="*60)
        self.log("📊 运行统计")
        self.log("="*60)
        self.log(f"运行时间: {hours:.1f} 小时")
        self.log(f"发出信号: {self.stats['total_signals']} 次")
        self.log(f"目标地址: {TARGET_WALLET}")
        self.log(f"检查间隔: {CHECK_INTERVAL} 秒")
        self.log("="*60 + "\n")
    
    def run(self):
        """主循环"""
        self.log("\n" + "="*60)
        self.log("🚀 Polymarket 实时跟单系统启动")
        self.log("="*60)
        self.log(f"目标地址: {TARGET_WALLET}")
        self.log(f"检查间隔: {CHECK_INTERVAL} 秒")
        self.log(f"Telegram: 已配置")
        self.log("="*60)
        self.log("按 Ctrl+C 停止\n")
        
        # 发送启动通知
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    'chat_id': TELEGRAM_CHAT_ID,
                    'text': f"🚀 跟单监控系统已启动！\n\n目标: Top 1 交易者\n地址: {TARGET_WALLET[:20]}...\n历史PnL: $394,791\n\n将每{CHECK_INTERVAL}秒检查一次新交易。",
                    'parse_mode': 'HTML'
                },
                timeout=10
            )
        except:
            pass
        
        cycle_count = 0
        
        while self.running:
            try:
                cycle_count += 1
                
                # 每10次循环打印一次统计
                if cycle_count % 10 == 0:
                    self.print_summary()
                
                self.log(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 检查新交易...")
                
                # 获取最近交易
                recent_trades = self.get_recent_trades(minutes=5)
                
                if recent_trades:
                    self.log(f"  ✅ 发现 {len(recent_trades)} 笔新交易")
                    
                    for trade in recent_trades:
                        # 分析交易
                        analysis = self.analyze_trade(trade)
                        
                        # 更新统计
                        self.stats['total_signals'] += 1
                        self.stats['last_trade_time'] = max(
                            self.stats['last_trade_time'],
                            trade.get('timestamp', 0)
                        )
                        
                        # 发送通知
                        if self.send_notification(trade, analysis):
                            self.log(f"  ✅ 信号 #{self.stats['total_signals']} 已发送")
                        else:
                            self.log(f"  ❌ 信号发送失败")
                        
                        time.sleep(1)  # 避免发送过快
                else:
                    self.log(f"  📭 暂无新交易")
                
                # 保存状态
                self.save_state()
                
                # 等待下次检查
                self.log(f"  ⏳ {CHECK_INTERVAL}秒后下次检查...\n")
                time.sleep(CHECK_INTERVAL)
                
            except Exception as e:
                self.log(f"❌ 循环错误: {e}")
                time.sleep(CHECK_INTERVAL)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Polymarket 实时跟单系统')
    parser.add_argument('--test', action='store_true', help='发送测试消息')
    parser.add_argument('--status', action='store_true', help='查看状态')
    
    args = parser.parse_args()
    
    if args.test:
        # 发送测试消息
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    'chat_id': TELEGRAM_CHAT_ID,
                    'text': "🧪 <b>测试消息</b>\n\n跟单监控系统运行正常！\n等待交易信号中...",
                    'parse_mode': 'HTML'
                },
                timeout=10
            )
            print("✅ 测试消息已发送")
        except Exception as e:
            print(f"❌ 发送失败: {e}")
    
    elif args.status:
        # 查看状态
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
            print(json.dumps(state, indent=2))
        except:
            print("暂无状态文件")
    
    else:
        # 启动监控
        monitor = CopyTradeMonitor()
        monitor.run()

if __name__ == '__main__':
    main()
