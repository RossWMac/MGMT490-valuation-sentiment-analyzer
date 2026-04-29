import json
import os
import random
from datetime import datetime, timedelta
import urllib.request
import xml.etree.ElementTree as ET

def get_assigned_date(index):
    now = datetime.now()
    if index < 3:
        days_ago = 1 + (index * 2)
    elif index < 11:
        days_ago = 8 + ((index - 3) * 2.5)
    else:
        days_ago = 31 + ((index - 11) * 2.4)
    return now - timedelta(days=days_ago)

def fetch_live_news(ticker):
    items = []
    try:
        url = f"https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            # Find all item elements
            for channel in root.findall('channel'):
                for item in channel.findall('item')[:3]:
                    title = item.find('title').text if item.find('title') is not None else ""
                    link = item.find('link').text if item.find('link') is not None else ""
                    source = item.find('source').text if item.find('source') is not None else "Live News"
                    
                    # deterministic pseudo-sentiment
                    random.seed(title)
                    score = (random.random() * 2) - 1
                    
                    items.append({
                        'title': title,
                        'source': source,
                        'url': link,
                        'score': score,
                        'date': datetime.now(),
                        'type': 'live'
                    })
    except Exception as e:
        pass # silently fallback to static data
    return items

def get_sentiment_data(ticker, days_window=30, source_type='all'):
    ticker = ticker.upper()
    all_items = []
    
    # 1. Try to fetch 3 live items (Live items are considered 'news')
    if source_type in ['all', 'news']:
        all_items.extend(fetch_live_news(ticker))
    
    # 2. Load from static DB to simulate historical sentiment
    db_path = os.path.join(os.path.dirname(__file__), "real_news_data.json")
    if os.path.exists(db_path):
        with open(db_path, "r") as f:
            db = json.load(f)
            
        if ticker in db:
            for i, real_item in enumerate(db[ticker]):
                date = get_assigned_date(i)
                days_ago = (datetime.now() - date).days
                
                if days_ago <= days_window:
                    publisher = real_item.get('publisher', 'Database')
                    item_type = 'social' if publisher in ['Reddit', 'X (formerly Twitter)', 'StockTwits'] else 'news'
                    
                    if source_type == 'all' or source_type == item_type:
                        # Same pseudo-score logic as JS
                        sentiment_score = ((i * 137) % 200 - 100) / 100.0
                        all_items.append({
                            'title': real_item.get('text', 'News Update'),
                            'source': publisher,
                            'url': real_item.get('url', '#'),
                            'score': sentiment_score,
                            'date': date,
                            'type': item_type
                        })
        else:
            # Generic fallback
            for i in range(15):
                date = get_assigned_date(i * 2)
                days_ago = (datetime.now() - date).days
                if days_ago <= days_window:
                    random.seed(f"{ticker}-seed-{i}")
                    is_news = random.random() > 0.5
                    item_type = 'news' if is_news else 'social'
                    
                    if source_type == 'all' or source_type == item_type:
                        score = (random.random() * 2) - 1
                        all_items.append({
                            'title': f"Market update for {ticker}" if is_news else f"Social sentiment for {ticker}",
                            'source': "Financial News" if is_news else "Social Media",
                            'url': "#",
                            'score': score,
                            'date': date,
                            'type': item_type
                        })
                    
    # Sort by date descending
    all_items.sort(key=lambda x: x['date'], reverse=True)
    
    if len(all_items) == 0:
        return 0.0, []
        
    avg_score = sum([item['score'] for item in all_items]) / len(all_items)
    
    # Calculate trend data (buckets)
    bucket_count = min(10, days_window if days_window <= 10 else 10)
    trend = []
    
    if len(all_items) > 0:
        min_time = min(item['date'] for item in all_items)
        max_time = max(item['date'] for item in all_items)
        # Avoid zero division if min_time == max_time
        time_diff = (max_time - min_time).total_seconds()
        bucket_size = time_diff / bucket_count if time_diff > 0 else 1.0
        
        for i in range(bucket_count):
            bucket_start = min_time + timedelta(seconds=i * bucket_size)
            bucket_end = min_time + timedelta(seconds=(i + 1) * bucket_size)
            
            # For the last bucket, include items exactly equal to max_time
            if i == bucket_count - 1:
                items_in_bucket = [item for item in all_items if bucket_start <= item['date'] <= bucket_end]
            else:
                items_in_bucket = [item for item in all_items if bucket_start <= item['date'] < bucket_end]
                
            bucket_avg = sum([item['score'] for item in items_in_bucket]) / len(items_in_bucket) if len(items_in_bucket) > 0 else 0
            display_date = bucket_start.strftime("%b %d")
            
            trend.append({
                'name': display_date,
                'score': round(bucket_avg, 2)
            })
    
    return avg_score, all_items, trend
