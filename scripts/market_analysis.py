#!/usr/bin/env python3
"""
Polymarket 市场分析工具
功能：获取热门市场、分析赔率趋势、流动性分析
"""

import argparse
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List

GAMMA_API_URL = "https://gamma-api.polymarket.com"
DATA_API_URL = "https://data-api.polymarket.com"

class PolymarketMarketAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})
    
    def get_active_markets(self, limit: int = 50) -> List[Dict]:
        """获取活跃市场"""
        try:
            resp = self.session.get(
                f"{GAMMA_API_URL}/events",
                params={
                    'active': 'true',
                    'closed': 'false',
                    'limit': limit,
                    'sort': 'volume',
                    'order': 'desc'
                },
                timeout=30
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"❌ 获取市场失败: {e}")
            return []
    
    def get_market_orderbook(self, token_id: str) -> Dict:
        """获取订单簿数据"""
        try:
            resp = self.session.get(
                f"https://clob.polymarket.com/book",
                params={'token_id': token_id},
                timeout=10
            )
            resp.raise_for_status()
            return resp.json()
        except:
            return {}
    
    def get_price_history(self, token_id: str, days: int = 7) -> List[Dict]:
        """获取价格历史"""
        try:
            end = int(datetime.now().timestamp())
            start = int((datetime.now() - timedelta(days=days)).timestamp())
            
            resp = self.session.get(
                f"https://clob.polymarket.com/prices/history",
                params={
                    'token_id': token_id,
                    'start': start,
                    'end': end,
                    'interval': '1d'
                },
                timeout=10
            )
            resp.raise_for_status()
            return resp.json().get('history', [])
        except:
            return []
    
    def analyze_volume_trend(self, markets: List[Dict]) -> List[Dict]:
        """分析成交量趋势"""
        analyzed = []
        
        for market in markets:
            volume = market.get('volume', 0)
            liquidity = market.get('liquidity', 0)
            
            # 计算流动性评分 (0-100)
            liquidity_score = min(100, (liquidity / 100000) * 100) if liquidity else 0
            
            analyzed.append({
                'id': market.get('id'),
                'title': market.get('title', 'Unknown'),
                'slug': market.get('slug', ''),
                'volume': volume,
                'liquidity': liquidity,
                'liquidity_score': round(liquidity_score, 1),
                'end_date': market.get('endDate'),
                'category': market.get('category', 'General')
            })
        
        return sorted(analyzed, key=lambda x: x['volume'], reverse=True)
    
    def analyze_price_movement(self, markets: List[Dict]) -> List[Dict]:
        """分析价格波动"""
        movers = []
        
        for market in markets:
            markets_data = market.get('markets', [])
            if not markets_data:
                continue
            
            for m in markets_data:
                token_id = m.get('tokenId')
                if not token_id:
                    continue
                
                # 获取价格历史
                history = self.get_price_history(token_id, days=3)
                
                if len(history) >= 2:
                    old_price = history[0].get('price', 0.5)
                    new_price = history[-1].get('price', 0.5)
                    
                    if old_price > 0:
                        change = ((new_price - old_price) / old_price) * 100
                        
                        if abs(change) > 5:  # 波动超过5%
                            movers.append({
                                'title': market.get('title', 'Unknown')[:50],
                                'outcome': m.get('outcome', 'Unknown'),
                                'old_price': round(old_price, 3),
                                'new_price': round(new_price, 3),
                                'change': round(change, 2),
                                'direction': '📈' if change > 0 else '📉'
                            })
        
        return sorted(movers, key=lambda x: abs(x['change']), reverse=True)[:10]
    
    def analyze_market(self, min_volume: float = 10000) -> Dict:
        """完整市场分析"""
        print("🔍 正在获取市场数据...")
        
        markets = self.get_active_markets(limit=100)
        
        if not markets:
            print("❌ 未能获取市场数据")
            return {}
        
        print(f"✅ 获取到 {len(markets)} 个活跃市场")
        print()
        
        # 筛选高成交量市场
        high_volume_markets = [m for m in markets if m.get('volume', 0) >= min_volume]
        
        # 分析成交量排名
        volume_ranking = self.analyze_volume_trend(high_volume_markets[:20])
        
        # 分析价格波动
        print("📊 分析价格波动...")
        price_movers = self.analyze_price_movement(markets[:30])
        
        # 统计信息
        total_volume = sum(m.get('volume', 0) for m in markets)
        total_liquidity = sum(m.get('liquidity', 0) for m in markets)
        
        # 分类统计
        categories = {}
        for m in markets:
            cat = m.get('category', 'Other')
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            'analysis_time': datetime.now().isoformat(),
            'total_active_markets': len(markets),
            'high_volume_markets': len(high_volume_markets),
            'total_volume': round(total_volume, 2),
            'total_liquidity': round(total_liquidity, 2),
            'top_markets': volume_ranking[:10],
            'price_movers': price_movers,
            'categories': categories
        }
    
    def format_output(self, result: Dict, format_type: str = 'text') -> str:
        """格式化输出"""
        if not result:
            return "❌ 分析失败"
        
        if format_type == 'telegram':
            output = f"📊 <b>Polymarket 市场分析</b>\n\n"
            output += f"📈 活跃市场: <b>{result['total_active_markets']}</b>\n"
            output += f"💰 总成交量: <b>${result['total_volume']:,.0f}</b>\n"
            output += f"💧 总流动性: <b>${result['total_liquidity']:,.0f}</b>\n\n"
            
            output += "🏆 <b>热门市场 (按成交量)</b>\n"
            for i, m in enumerate(result['top_markets'][:5], 1):
                title = m['title'][:40] + '...' if len(m['title']) > 40 else m['title']
                output += f"{i}. {title}\n"
                output += f"   💰 ${m['volume']:,.0f} | 💧 {m['liquidity_score']}/100\n\n"
            
            if result['price_movers']:
                output += "⚡ <b>价格波动 (24h)</b>\n"
                for m in result['price_movers'][:5]:
                    output += f"{m['direction']} {m['title'][:30]}...\n"
                    output += f"   {m['old_price']} → {m['new_price']} ({m['change']}%)\n\n"
        
        else:
            output = f"📊 Polymarket 市场分析报告\n"
            output += f"{'='*50}\n\n"
            output += f"分析时间: {result['analysis_time']}\n"
            output += f"活跃市场: {result['total_active_markets']}\n"
            output += f"高成交量市场: {result['high_volume_markets']}\n"
            output += f"总成交量: ${result['total_volume']:,.2f}\n"
            output += f"总流动性: ${result['total_liquidity']:,.2f}\n\n"
            
            output += "🏆 热门市场 (按成交量)\n"
            for i, m in enumerate(result['top_markets'][:10], 1):
                output += f"  {i}. {m['title'][:50]}\n"
                output += f"     成交量: ${m['volume']:,.2f}\n"
                output += f"     流动性: {m['liquidity_score']}/100\n\n"
            
            if result['price_movers']:
                output += "\n⚡ 价格波动 (24h)\n"
                for m in result['price_movers']:
                    direction = "📈" if m['change'] > 0 else "📉"
                    output += f"  {direction} {m['title'][:40]}\n"
                    output += f"     变化: {m['change']}%\n"
                    output += f"     {m['old_price']} → {m['new_price']}\n\n"
            
            output += "\n📂 市场分类\n"
            for cat, count in sorted(result['categories'].items(), key=lambda x: x[1], reverse=True):
                output += f"  {cat}: {count}\n"
        
        return output

def main():
    parser = argparse.ArgumentParser(description='Polymarket 市场分析工具')
    parser.add_argument('--min-volume', type=float, default=10000, 
                        help='最小成交量过滤')
    parser.add_argument('--output-format', choices=['text', 'telegram', 'json'],
                        default='text')
    parser.add_argument('--output', '-o', help='输出文件')
    
    args = parser.parse_args()
    
    analyzer = PolymarketMarketAnalyzer()
    result = analyzer.analyze_market(args.min_volume)
    
    if not result:
        print("❌ 分析失败")
        return
    
    if args.output_format == 'json':
        output = json.dumps(result, indent=2, ensure_ascii=False)
    else:
        output = analyzer.format_output(result, args.output_format)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"✅ 结果已保存: {args.output}")
    else:
        print(output)

if __name__ == '__main__':
    main()
