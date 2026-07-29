import requests
import pandas as pd
from datetime import datetime
import re
import json
import os
import xml.etree.ElementTree as ET

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
    """百度热搜"""
    url = "https://top.baidu.com/board?tab=realtime"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = 'utf-8'
        titles = re.findall(r'<div class="c-single-text-ellipsis">(.*?)</div>', resp.text)
        if not titles:
            titles = re.findall(r'"title":"(.*?)"', resp.text)
        
        items = []
        for title in titles:
            title = title.strip()
            if len(title) > 3 and match_keywords(title):
                items.append({
                    'platform': '百度热搜',
                    'title': title,
                    'timestamp': datetime.now().isoformat()
                })
        print(f"  百度热搜获取 {len(titles)} 条，命中 {len(items)} 条")
        return items
    except Exception as e:
        print(f"  百度热搜出错: {e}")
        return []

def get_zhihu_hot():
    """知乎热榜"""
    url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
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
        print(f"  知乎热榜获取 {len(data.get('data', []))} 条，命中 {len(items)} 条")
        return items
    except Exception as e:
        print(f"  知乎热榜出错: {e}")
        return []

def get_douyin_hot():
    """抖音热点（通过 RSSHub）"""
    url = "https://rsshub.app/douyin/hot"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        root = ET.fromstring(resp.text)
        items = []
        for item in root.findall('.//item'):
            title = item.find('title').text
            if title and match_keywords(title):
                items.append({
                    'platform': '抖音热点',
                    'title': title,
                    'timestamp': datetime.now().isoformat()
                })
        print(f"  抖音热点获取 {len(root.findall('.//item'))} 条，命中 {len(items)} 条")
        return items
    except Exception as e:
        print(f"  抖音热点出错: {e}")
        return []

def get_xiaohongshu_hot():
    """小红书热榜（目前返回空，需要后续优化）"""
    print("  ⚠️ 小红书热榜需要登录+反爬，暂无法直接获取")
    return []

def main():
    all_items = []
    print("=" * 50)
    print("🌊 外滩舆情热词感知系统 v2.0")
    print("=" * 50)
    print("开始采集...\n")
    
    print("📱 [1/4] 正在抓取百度热搜...")
    all_items.extend(get_baidu_hot())
    
    print("📱 [2/4] 正在抓取知乎热榜...")
    all_items.extend(get_zhihu_hot())
    
    print("📱 [3/4] 正在抓取抖音热点...")
    all_items.extend(get_douyin_hot())
    
    print("📱 [4/4] 正在抓取小红书热榜...")
    all_items.extend(get_xiaohongshu_hot())
    
    if all_items:
        df_new = pd.DataFrame(all_items)
        
        if os.path.exists('hot_words.csv'):
            df_existing = pd.read_csv('hot_words.csv')
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined.to_csv('hot_words.csv', index=False, encoding='utf-8-sig')
            print(f"\n✅ 追加采集完毕，新增 {len(df_new)} 条，总计 {len(df_combined)} 条")
        else:
            df_new.to_csv('hot_words.csv', index=False, encoding='utf-8-sig')
            print(f"\n✅ 采集完毕，共发现 {len(df_new)} 条与外滩相关的热点。")
        
        print("\n📋 命中的热词：")
        for _, row in df_new.iterrows():
            print(f"  [{row['platform']}] {row['title']}")
    else:
        print("\n⚠️ 当前未发现外滩相关热词。")
        if not os.path.exists('hot_words.csv'):
            df = pd.DataFrame([{
                'platform': '测试',
                'title': '暂无热点数据，请检查爬虫配置',
                'timestamp': datetime.now().isoformat()
            }])
            df.to_csv('hot_words.csv', index=False, encoding='utf-8-sig')
            print("  已生成测试文件 hot_words.csv")
        else:
            print("  📁 已有历史数据，保留不覆盖")

if __name__ == '__main__':
    main()
