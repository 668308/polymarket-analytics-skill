#!/usr/bin/env python3
"""
Polymarket 钱包监控通知系统
功能：监控目标钱包交易并发送Telegram通知
"""

import os
import sys
import time
import json
import requests
from datetime import datetime
from typing import List, Dict

# 配置
TARGET_WALLET = "0x2a2c53bd278c04da9962fcf96490e17f3dfb9bc1"
DATA_API_URL = "https://data-api.polymarket.com"
CHECK_INTERVAL = 300  # 5分钟检查一次

# Telegram 配置
TELEGRAM_BOT_TOKEN = "8412543152:AAGVHlrK8edkXvCv6RwSjcFBZYpLdsvffSY"
TELEGRAM_CHAT_ID = "8188236210"

# 状态文件
STATE_FILE = "/tmp/monitor_top1_state.json"

class WalletMonitor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})
        self.last_check_time = self.load_state()
        
    def load_state(self) -> int:
        """加载上次检查时间"""
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, 'r') as f:
                    state = json.load(f)
                    return state.get('last_timestamp', 0)
        except:
            pass
        return int(time.time()) - 3600  # 默认1小时前
    
    def save_state(self, timestamp: int):
        """保存状态"""
        with open(STATE_FILE, 'w') as f:
            json.dump({'last_timestamp': timestamp}, f)
    
    def get_recent_trades(self) -> List[Dict]:
        """获取目标钱包的最近交易"""
        try:
            resp = self.session.get(
                f"{DATA_API_URL}/trades",
                params={
                    'user': TARGET_WALLET,
                    'limit': 20
                },
                timeout=30
            )
            
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"❌ 获取交易失败: {e}")
        
        return []
    
    def format_notification(self, trade: Dict) -> str:
        """格式化通知消息"""
        side = trade.get('side', 'UNKNOWN')
        price = trade.get('price', 0)
        size = trade.get('size', 0)
        title = trade.get('title', 'Unknown Market')
        outcome = trade.get('outcome', '')
        
        # 建议逻辑
        if price < 0.5:
            suggestion = "✅ 强烈建议跟单 (价格 < 0.5，安全边际高)"
        elif price < 0.6:
            suggestion = "✅ 建议跟单 (价格合理)"
        elif price < 0.7:
            suggestion = "🟡 谨慎跟单 (价格中等)"
        else:
            suggestion = "❌ 不建议跟单 (价格过高，风险大)"
        
        emoji = "🟢" if side == "BUY" else "🔴"
        
        message = f"""
{emoji} <b>Polymarket 跟单信号</b>

👤 <b>目标钱包</b>: <code>{TARGET_WALLET[:20]}...</code>
📊 <b>操作类型</b>: {side}
🎯 <b>交易市场</b>: {title[:40]}
📈 <b>预测结果</b>: {outcome}
💰 <b>交易价格</b>: ${price:.3f}
📦 <b>交易数量</b>: {size}
⏰ <b>时间</b>: {datetime.now().strftime('%H:%M:%S')}

💡 <b>建议</b>:
{suggestion}

📋 <b>跟单规则</b>:
• 价格 < 0.5: 跟单10% ($100)
• 价格 0.5-0.6: 跟单5% ($50)
• 价格 > 0.7: 不跟单
• 设置止盈: +20%卖出一半
• 设置止损: -15%全部卖出

🔗 <a href='https://polymarket.com'>前往 Polymarket 交易</a>
"""
        return message
    
    def send_telegram_notification(self, message: str):
        """发送Telegram通知"""
        try:
            resp = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    'chat_id': TELEGRAM_CHAT_ID,
                    'text': message,
                    'parse_mode': 'HTML',
                    'disable_web_page_preview': False
                },
                timeout=10
            )
            return resp.json().get('ok', False)
        except Exception as e:
            print(f"❌ 发送通知失败: {e}")
            return False
    
    def check_and_notify(self):
        """检查新交易并发送通知"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 检查新交易...")
        
        trades = self.get_recent_trades()
        
        if not trades:
            print("  暂无交易数据")
            return
        
        # 筛选新交易
        new_trades = []
        latest_timestamp = self.last_check_time
        
        for trade in trades:
            timestamp = trade.get('timestamp', 0)
            if timestamp > self.last_check_time:
                new_trades.append(trade)
                if timestamp > latest_timestamp:
                    latest_timestamp = timestamp
        
        # 发送通知
        if new_trades:
            print(f"  ✅ 发现 {len(new_trades)} 笔新交易")
            for trade in new_trades:
                message = self.format_notification(trade)
                if self.send_telegram_notification(message):
                    print(f"  ✅ 已发送: {trade.get('side')} {trade.get('title', 'Unknown')[:30]}")
                else:
                    print(f"  ❌ 发送失败")
                time.sleep(1)  # 避免发送过快
        else:
            print("  📭 暂无新交易")
        
        # 更新状态
        self.last_check_time = latest_timestamp
        self.save_state(latest_timestamp)
    
    def run(self):
        """主循环"""
        print("="*60)
        print("🚀 Polymarket 钱包监控启动")
        print("="*60)
        print(f"目标钱包: {TARGET_WALLET}")
        print(f"检查间隔: {CHECK_INTERVAL}秒")
        print(f"Telegram: 已配置")
        print("="*60)
        print("\n按 Ctrl+C 停止\n")
        
        try:
            while True:
                self.check_and_notify()
                print(f"  ⏳ {CHECK_INTERVAL}秒后下次检查...\n")
                time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\n\n🛑 监控已停止")
            print("="*60)

def main():
    """入口函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Polymarket 钱包监控')
    parser.add_argument('--once', action='store_true', help='只检查一次')
    parser.add_argument('--test', action='store_true', help='发送测试消息')
    
    args = parser.parse_args()
    
    monitor = WalletMonitor()
    
    if args.test:
        # 发送测试消息
        test_message = """
🧪 <b>测试消息</b>

监控已启动！
我将每5分钟检查目标钱包的新交易。

👤 目标: <code>0x2a2c...9bc1</code>
💰 历史PnL: $394,791.51
🎯 领域: 体育赛事预测

等待交易信号中...
"""
        monitor.send_telegram_notification(test_message)
        print("✅ 测试消息已发送")
    elif args.once:
        monitor.check_and_notify()
    else:
        monitor.run()

if __name__ == '__main__':
    main()
