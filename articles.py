import os
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from slugify import slugify
import hashlib
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "markdown_articles")
META_PATH = os.path.join(OUTPUT_DIR, "meta.json")
ACTIVITY_PATH = os.path.join(BASE_DIR, "activity.log")

def write_log(log_info):
    log_line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Added: {log_info['added']} | Updated: {log_info['updated']} | Skipped: {log_info['skipped']}"
    with open(ACTIVITY_PATH, "a") as log_file:
        log_file.write(log_line + "\n")

def save_meta(meta):
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

def load_meta():
    if os.path.exists(META_PATH):
        with open(META_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def compute_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def get_articles():
    url = "https://support.optisigns.com/api/v2/help_center/en-us/articles.json?per_page=40"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def clean_html_to_markdown(html):
    soup = BeautifulSoup(html, "html.parser")

    for selector in ['nav', 'footer', 'aside', '.ads', '.header', '.footer']:
        for tag in soup.select(selector):
            tag.decompose()

    html_clean = str(soup)

    markdown = md(html_clean, strip=['a'])
    return markdown.strip()

def save_as_markdown(article, log_info, meta):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    title = article["title"]
    html_body = article["body"]
    markdown_body = clean_html_to_markdown(html_body)
    current_hash = compute_hash(markdown_body)

    slug = slugify(title)
    filename = f"{slug}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)

    previous_hash = meta.get(filename)

    if not previous_hash:
        log_info["added"] += 1
    elif previous_hash != current_hash:
        log_info["updated"] += 1
    else:
        log_info["skipped"] += 1
        return
    

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(markdown_body)

    meta[filename] = current_hash

def main():
    print("Running successfully...")
    data = get_articles()
    meta = load_meta()
    log_info = {"added": 0, "updated": 0, "skipped": 0}
    if data:
        articles = data['articles']
        for article in articles:
            save_as_markdown(article, log_info, meta)
    write_log(log_info)
    save_meta(meta)