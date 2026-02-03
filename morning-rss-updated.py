#!/usr/bin/env python3
"""
Updated RSS reader for morning news updates.
Always shows 5 headlines with summaries from each source, regardless of whether they're new.
"""

import urllib.request
import xml.etree.ElementTree as ET
import html
import sys
import re
from datetime import datetime

# RSS feeds for morning update
FEEDS = {
    "Democracy Now": "https://www.democracynow.org/democracynow.rss",
    "LA Times California": "https://www.latimes.com/california/rss2.0.xml", 
    "The Intercept": "https://theintercept.com/feed/"
}

def parse_date(date_string):
    """Parse various RSS date formats."""
    if not date_string:
        return "Unknown date"
    
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
            return parsed.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    # Handle "Z" suffix (UTC)
    if date_string.endswith('Z'):
        try:
            parsed = datetime.strptime(date_string[:-1], '%Y-%m-%dT%H:%M:%S')
            return parsed.strftime('%Y-%m-%d')
        except ValueError:
            pass
    
    return "Unknown date"

def clean_html(text):
    """Clean HTML tags and entities from text."""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Decode HTML entities
    text = html.unescape(text)
    # Remove excess whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def truncate_summary(text, max_length=150):
    """Truncate text to max_length and add ellipsis if needed."""
    if not text:
        return "No summary available"
    if len(text) <= max_length:
        return text
    # Try to find a space near the max_length to avoid cutting words
    cutoff = text.rfind(' ', max_length-20, max_length)
    if cutoff == -1:  # No space found, just cut at max_length
        cutoff = max_length
    return text[:cutoff] + "..."

def fetch_feed(name, url, max_articles=5):
    """Fetch and parse RSS feed, return the most recent articles."""
    try:
        print(f"📰 {name}")
        print("-" * 30)
        
        # Fetch the RSS feed
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_content = response.read().decode('utf-8')
        
        # Parse XML
        root = ET.fromstring(xml_content)
        
        articles = []
        
        # Find all item tags (works for both RSS and Atom feeds)
        items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
        
        for item in items[:max_articles]:
            # Extract title
            title_elem = item.find('title')
            if title_elem is None:
                title_elem = item.find('.//{http://www.w3.org/2005/Atom}title')
            title = title_elem.text if title_elem is not None and title_elem.text else 'No title'
            title = clean_html(title)
            
            # Extract link
            link_elem = item.find('link')
            if link_elem is None:
                link_elem = item.find('.//{http://www.w3.org/2005/Atom}link[@rel="alternate"]')
            
            link = ''
            if link_elem is not None:
                link = link_elem.text if link_elem.text else link_elem.get('href', '')
            
            # Extract date
            date_elem = item.find('pubDate')
            if date_elem is None:
                date_elem = item.find('.//{http://purl.org/dc/elements/1.1/}date')
            if date_elem is None:
                date_elem = item.find('.//{http://www.w3.org/2005/Atom}published')
            if date_elem is None:
                date_elem = item.find('.//{http://www.w3.org/2005/Atom}updated')
            
            pub_date = "Unknown date"
            if date_elem is not None and date_elem.text:
                pub_date = parse_date(date_elem.text)
            
            # Extract summary/description
            desc_elem = item.find('description')
            if desc_elem is None:
                desc_elem = item.find('.//{http://www.w3.org/2005/Atom}summary')
            if desc_elem is None:
                desc_elem = item.find('.//{http://www.w3.org/2005/Atom}content')
            
            summary = "No summary available"
            if desc_elem is not None and desc_elem.text:
                summary = clean_html(desc_elem.text)
                summary = truncate_summary(summary)
            
            # Print article details
            print(f"{len(articles) + 1}. {title}")
            print(f"   📅 {pub_date}")
            print(f"   📝 {summary}")
            print()
            
            articles.append({
                'title': title,
                'url': link.strip(),
                'date': pub_date,
                'summary': summary
            })
        
        if not articles:
            print("   No articles found for this feed")
            print()
        
        return articles
        
    except Exception as e:
        print(f"❌ Error fetching {name}: {e}")
        print()
        return []

def get_morning_news(max_per_feed=5):
    """Get morning news update from all feeds."""
    print("🌅 DAILY NEWS HEADLINES")
    print("=" * 50)
    
    all_articles = []
    
    for feed_name, feed_url in FEEDS.items():
        articles = fetch_feed(feed_name, feed_url, max_per_feed)
        all_articles.extend(articles)
    
    print(f"📊 Total: {len(all_articles)} articles")
    return all_articles

if __name__ == "__main__":
    max_articles = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    get_morning_news(max_articles)