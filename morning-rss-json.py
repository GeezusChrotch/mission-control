#!/usr/bin/env python3
"""
RSS fetcher for morning briefing - outputs JSON for parsing.
Fetches latest 5 articles from each configured source.
"""

import urllib.request
import xml.etree.ElementTree as ET
import json
import html
import re
from datetime import datetime, timedelta

def get_text(elem):
    """Extract text from element, handling CDATA."""
    if elem is None:
        return ''
    # itertext() gets all text including from CDATA
    return ''.join(elem.itertext()).strip()

def fetch_feed(name, url, max_articles=5):
    """Fetch and parse RSS feed, return latest N articles."""
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        })
        with urllib.request.urlopen(req, timeout=15) as response:
            xml_content = response.read().decode('utf-8')
        
        root = ET.fromstring(xml_content)
        articles = []
        
        # Find all items (RSS and Atom)
        items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
        
        for item in items[:max_articles]:
            # Title (handle CDATA)
            title_elem = item.find('title')
            if title_elem is None:
                title_elem = item.find('.//{http://www.w3.org/2005/Atom}title')
            title = get_text(title_elem) or 'No title'
            
            # Link
            link_elem = item.find('link')
            if link_elem is None:
                link_elem = item.find('.//{http://www.w3.org/2005/Atom}link')
            if link_elem is not None:
                link = link_elem.text if link_elem.text else link_elem.get('href', '')
            else:
                link = ''
            
            # Summary/description (handle CDATA)
            desc_elem = item.find('description')
            if desc_elem is None:
                desc_elem = item.find('.//{http://www.w3.org/2005/Atom}summary')
            if desc_elem is None:
                desc_elem = item.find('.//{http://www.w3.org/2005/Atom}content')
            
            desc_text = get_text(desc_elem)
            summary = ''
            if desc_text:
                # Strip HTML and truncate
                clean = re.sub(r'<[^>]+>', '', desc_text)
                clean = html.unescape(clean).strip()
                # Get first sentence or first 150 chars
                sentences = clean.split('. ')
                if sentences:
                    summary = sentences[0]
                    if len(summary) > 150:
                        summary = summary[:147] + '...'
                    elif len(sentences) > 1 and len(summary) < 80:
                        summary += '. ' + sentences[1][:70]
                else:
                    summary = clean[:150] + '...' if len(clean) > 150 else clean
            
            articles.append({
                'title': html.unescape(title),
                'url': link.strip(),
                'summary': summary
            })
        
        return {'source': name, 'articles': articles}
        
    except Exception as e:
        return {'source': name, 'error': str(e), 'articles': []}

def main():
    import sys
    
    # Parse arguments: [max_articles] [source1,source2,...]
    max_articles = 3  # Default: 3 stories per source
    requested_sources = None
    
    if len(sys.argv) > 1:
        try:
            max_articles = int(sys.argv[1])
        except ValueError:
            requested_sources = sys.argv[1].split(',')
    
    if len(sys.argv) > 2:
        requested_sources = sys.argv[2].split(',')
    
    all_feeds = [
        ("Democracy Now", "https://www.democracynow.org/democracynow.rss"),
        ("LA Times California", "https://www.latimes.com/california/rss2.0.xml"),
        ("The Intercept", "https://theintercept.com/feed/")
    ]
    
    # Filter feeds if specific sources requested
    if requested_sources:
        feeds = [(name, url) for name, url in all_feeds 
                 if any(req.lower() in name.lower() for req in requested_sources)]
    else:
        feeds = all_feeds
    
    results = []
    for name, url in feeds:
        result = fetch_feed(name, url, max_articles=max_articles)
        results.append(result)
    
    # Output JSON for parsing by the briefing generator
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
