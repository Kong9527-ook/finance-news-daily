import feedparser
import requests
import os
from datetime import datetime

# ========== 从环境变量读取Token ==========
PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN")

def fetch_news():
    """组合多个国内可用的RSS源"""
    print("=" * 50)
    print("📡 正在抓取多源新闻...")
    print("=" * 50)
    
    news_items = []
    
    # 多个国内RSS源
    rss_sources = [
        {"name": "36氪", "url": "https://36kr.com/feed", "enabled": True},
        {"name": "爱范儿", "url": "https://www.ifanr.com/feed", "enabled": True},
        {"name": "虎嗅", "url": "https://www.huxiu.com/rss/0.xml", "enabled": True},
        {"name": "知乎每日精选", "url": "https://www.zhihu.com/rss", "enabled": True},
    ]
    
    for source in rss_sources:
        if not source["enabled"]:
            continue
            
        try:
            print(f"\n正在抓取: {source['name']}")
            d = feedparser.parse(source["url"])
            
            count = 0
            for entry in d.entries[:3]:
                news_items.append({
                    'source': source['name'],
                    'title': entry.title,
                    'time': datetime.now().strftime('%Y-%m-%d'),
                    'url': entry.link,
                })
                count += 1
                print(f"  ✓ {entry.title[:50]}...")
            
            print(f"  ✅ 成功获取 {count} 条")
            
        except Exception as e:
            print(f"  ❌ 抓取失败: {e}")
    
    return news_items

def push_to_wechat(content):
    """推送到微信"""
    url = "http://www.pushplus.plus/send"
    today = datetime.now().strftime("%Y-%m-%d")
    
    data = {
        "token": PUSHPLUS_TOKEN,
        "title": f"📰 财经早报 {today}",
        "content": content,
        "template": "markdown"
    }
    
    response = requests.post(url, json=data)
    return response.json()

if __name__ == "__main__":
    print("=" * 60)
    print("📰 财经早报系统（多源版）启动")
    print("=" * 60)
    
    # 检查Token
    if not PUSHPLUS_TOKEN:
        print("❌ 错误：未设置PUSHPLUS_TOKEN环境变量")
        exit(1)
    
    # 1. 抓取新闻
    news_list = fetch_news()
    
    print(f"\n✅ 总计抓取 {len(news_list)} 条新闻")
    
    if not news_list:
        print("❌ 没有抓取到任何新闻，退出")
        exit(0)
    
    # 2. 生成推送内容
    content = f"## 📊 财经早报 {datetime.now().strftime('%Y-%m-%d')}\n\n"
    
    for i, news in enumerate(news_list[:15], 1):
        content += f"{i}. **{news['source']}**：{news['title']}\n"
    
    # 3. 推送
    print("\n📱 正在推送...")
    result = push_to_wechat(content)
    
    if result.get('code') == 200:
        print("✅ 推送成功！请查看微信")
    else:
        print(f"❌ 推送失败: {result}")
