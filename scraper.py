import urllib.request
import re
import json
import ssl
import os

def scrape_gikai_news():
    url = "https://www.town.shimanto.lg.jp/gikai/"
    print(f"Fetching {url}...")
    
    # Handle SSL certificates if necessary
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            html = response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return

    # Extract the block of newest info
    block_match = re.search(r'議会新着情報(.*?)(?:</ul>|</div>)', html, re.DOTALL)
    news_list = []
    
    if block_match:
        block = block_match.group(1)
        # Regex to find: <li>YYYY年MM月DD日 <a href="L">T</a></li>
        # Sometimes there's a space, sometimes a full-width space "　"
        items = re.findall(r'<li>\s*(\d{4}年\d{1,2}月\d{1,2}日).*?<a href="([^"]+)">(.*?)</a>', block, re.DOTALL)
        
        for date_str, link, title in items:
            if link.startswith('/'):
                link = "https://www.town.shimanto.lg.jp" + link
            # Clean up title (remove HTML tags if any)
            title = re.sub(r'<[^>]+>', '', title)
            news_list.append({
                "date": date_str.strip(),
                "title": title.strip(),
                "url": link.strip()
            })
            
    print(f"Found {len(news_list)} news items.")
    
    # Write to newsData.js
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(script_dir, "newsData.js")
    
    js_content = "const GIKAI_NEWS = " + json.dumps(news_list, ensure_ascii=False, indent=2) + ";\n"
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(js_content)
        
    print(f"Successfully wrote data to {out_path}")

if __name__ == "__main__":
    scrape_gikai_news()
