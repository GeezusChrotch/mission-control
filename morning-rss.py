#!/usr/bin/env python3
"""
Simple RSS reader for morning news updates.
Fetches and summarizes recent articles from configured feeds.
"""

import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import sys
import html
from datetime import datetime, timedelta
from pathlib import Path
import re

# RSS feeds for morning update
FEEDS = {
    "Democracy Now": "https://www.democracynow.org/podcast.xml",
    "LA Times California": "https://www.latimes.com/california/rss2.0.xml", 
    "The Intercept": "https://theintercept.com/feed/"
}

# Cache file to track what we've seen
CACHE_FILE = Path.home() / ".clawd-rss-cache.json"

def load_cache():
    """Load previously seen article URLs."""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache):
    """Save seen article URLs."""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save cache: {e}")

def parse_date(date_string):
    """Parse various RSS date formats."""
    if not date_string:
        return None
    
    # Clean up the date string
    date_string = date_string.strip()
    
    # Common RSS date formats
    formats = [
        '%a, %d %b %Y %H:%M:%S %Z',
        '%a, %d %b %Y %H:%M:%S %z', 
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%d %H:%M:%S',
        '%d %b %Y %H:%M:%S',
        '%a, %d %b %Y %H:%M:%S GMT',
        '%a, %d %b %Y %H:%M:%S EST',
        '%a, %d %b %Y %H:%M:%S PST'
    ]
    
    for fmt in formats:
        try:
            parsed = datetime.strptime(date_string, fmt)
            # Convert timezone-aware dates to naive for comparison
            if parsed.tzinfo is not None:
                parsed = parsed.replace(tzinfo=None)
            return parsed
        except ValueError:
            continue
    
    # Handle "Z" suffix (UTC)
    if date_string.endswith('Z'):
        try:
            parsed = datetime.strptime(date_string[:-1], '%Y-%m-%dT%H:%M:%S')
            return parsed
        except ValueError:
            pass
    
    return None

def fetch_feed(name, url, hours=24):
    """Fetch and parse RSS feed, return recent articles."""
    try:
        print(f"📡 Fetching {name}...")
        
        # Fetch the RSS feed
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_content = response.read().decode('utf-8')
        
        # Parse XML
        root = ET.fromstring(xml_content)
        
        articles = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Find all item tags (works for both RSS and Atom feeds)
        items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
        
        for item in items:
            # Extract title
            title_elem = item.find('title')
            if title_elem is None:
                title_elem = item.find('.//{http://www.w3.org/2005/Atom}title')
            title = title_elem.text if title_elem is not None and title_elem.text else 'No title'
            
            # Extract link
            link_elem = item.find('link')
            if link_elem is None:
                link_elem = item.find('.//{http://www.w3.org/2005/Atom}link[@rel="alternate"]')
            
            if link_elem is not None:
                link = link_elem.text if link_elem.text else link_elem.get('href', '')
            else:
                link = ''
            
            # Extract date
            date_elem = item.find('pubDate')
            if date_elem is None:
                date_elem = item.find('.//{http://purl.org/dc/elements/1.1/}date')
            if date_elem is None:
                date_elem = item.find('.//{http://www.w3.org/2005/Atom}published')
            if date_elem is None:
                date_elem = item.find('.//{http://www.w3.org/2005/Atom}updated')
            
            pub_date = None
            if date_elem is not None and date_elem.text:
                pub_date = parse_date(date_elem.text)
            
            # Extract summary/description
            desc_elem = item.find('description')
            if desc_elem is None:
                desc_elem = item.find('.//{http://www.w3.org/2005/Atom}summary')
            if desc_elem is None:
                desc_elem = item.find('.//{http://www.w3.org/2005/Atom}content')
            
            summary = ''
            if desc_elem is not None and desc_elem.text:
                # Strip HTML tags and truncate
                summary = re.sub(r'<[^>]+>', '', desc_elem.text)[:200] + '...' if len(desc_elem.text) > 200 else desc_elem.text
            
            # Include if recent or if we can't determine date  
            if pub_date is None or pub_date > cutoff_time:
                articles.append({
                    'title': html.unescape(title.strip()) if title else 'No title',
                    'url': link.strip(),
                    'date': pub_date.strftime('%Y-%m-%d %H:%M') if pub_date else 'Unknown',
                    'summary': html.unescape(summary.strip()) if summary else ''
                })
        
        print(f"✅ {name}: {len(articles)} recent articles")
        return articles
        
    except Exception as e:
        print(f"❌ Error fetching {name}: {e}")
        return []

def get_morning_update(hours=24, max_per_feed=5):
    """Get morning news update from all feeds."""
    print(f"🌅 Morning RSS Update - Last {hours} hours")
    print("=" * 50)
    
    cache = load_cache()
    all_new_articles = []
    
    for feed_name, feed_url in FEEDS.items():
        print(f"\n📰 {feed_name}")
        print("-" * 30)
        
        articles = fetch_feed(feed_name, feed_url, hours)
        
        # Check for new articles
        feed_cache_key = f"{feed_name}_seen"
        seen_urls = set(cache.get(feed_cache_key, []))
        new_articles = []
        
        for article in articles[:max_per_feed]:
            if article['url'] not in seen_urls:
                new_articles.append(article)
                seen_urls.add(article['url'])
        
        # Update cache
        cache[feed_cache_key] = list(seen_urls)
        
        # Display articles
        if new_articles:
            for i, article in enumerate(new_articles, 1):
                print(f"{i}. {article['title']}")
                print(f"   🔗 {article['url']}")
                print(f"   📅 {article['date']}")
                if article['summary']:
                    print(f"   📝 {article['summary']}")
                print()
            all_new_articles.extend(new_articles)
        else:
            print("   No new articles")
    
    # Save updated cache
    save_cache(cache)
    
    print(f"\n📊 Summary: {len(all_new_articles)} new articles total")
    return all_new_articles

if __name__ == "__main__":
    hours = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    get_morning_update(hours)