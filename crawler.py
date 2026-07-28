import requests
import pandas as pd
from datetime import datetime
import re
import json

# 读取关键词配置
with open('keywords.txt', 'r', encoding='utf-8') as f:
    raw_keywords = [line.strip() for line in f if line.strip()]

print(f"读取到 {len(raw_keywords)} 个关键词: {raw_keywords}")

single_keywords = []
combo_keywords = []
for kw in raw_keywords:
    if '+' in kw:
        combo_keywords.append(kw.split('+'))
    else:
        single_keywords.append(kw)

def match_keywords(text):
    """检查文本是否命中任一关键词组合"""
    if not text:
        return False
    text_lower = text.lower()
    for k in single_keywords:
        if k.lower() in text_lower:
            return True
    for combo in combo_keywords:
        if all(k.lower() in text_lower for k in combo):
            return True
    return False

def get_baidu_hot():
    """抓取百度热搜"""
    url = "https://top.baidu.com/board?tab=realtime"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = 'utf-8'
        # 尝试多种匹配方式
        titles = re.findall(r'<div class="c-single-text-ellipsis">(.*?)</div>', resp.text)
        if not titles:
            # 备用匹配方式
            titles = re.findall(r'"title":"(.*?)"', resp.text)
        if not titles:
            titles = re.findall(r'<a[^>]*>([^<]*外滩[^<]*)</a>', resp.text)
        
        items = []
        for title in titles:
            title = title.strip()
            if len(title) > 3 and match_keywords(title):
                items.append({
                    'platform': '百度热搜',
                    'title': title,
                    'timestamp': datetime.now().isoformat()
                })
        print(f"  百度热搜获取 {len(titles)} 条原始数据，命中 {len(items)} 条")
        return items
    except Exception as e:
        print(f"  百度热搜出错: {e}")
        return []

def get_zhihu_hot():
    """抓取知乎热榜"""
    url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        data = resp.json()
        items = []
        for item in data.get('data', []):
            title = item.get('target', {}).get('title', '')
            if match_keywords(title):
                items.append({
                    'platform': '知乎热榜',
                    'title': title,
                    'timestamp': datetime.now().isoformat()
                })
        print(f"  知乎热榜获取 {len(data.get('data', []))} 条原始数据，命中 {len(items)} 条")
        return items
    except Exception as e:
        print(f"  知乎热榜出错: {e}")
        return []

def main():
    all_items = []
    print("开始采集...")
    
    print("正在抓取百度热搜...")
    all_items.extend(get_baidu_hot())
    
    print("正在抓取知乎热榜...")
    all_items.extend(get_zhihu_hot())
    
    if all_items:
        df = pd.DataFrame(all_items)
        df.to_csv('hot_words.csv', index=False, encoding='utf-8-sig')
        print(f"\n采集完毕，共发现 {len(df)} 条与外滩相关的热点。")
        print("命中的热词：")
        for _, row in df.iterrows():
            print(f"  [{row['platform']}] {row['title']}")
    else:
        print("\n⚠️ 当前未发现外滩相关热词。请检查：")
        print("  1. keywords.txt 是否包含有效关键词")
        print("  2. 目标网站是否可访问")
        print("  3. 是否有网络连接问题")
        # 生成一个测试文件以便流程继续
        df = pd.DataFrame([{
            'platform': '测试',
            'title': '暂无热点数据，请检查爬虫配置',
            'timestamp': datetime.now().isoformat()
        }])
        df.to_csv('hot_words.csv', index=False, encoding='utf-8-sig')
        print("  已生成测试文件 hot_words.csv")

if __name__ == '__main__':
    main()
