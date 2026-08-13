import re
import feedparser
from email.utils import parsedate_to_datetime

from app.database import save_article


def get_image(entry):
    # 1. media_content
    if hasattr(entry, "media_content"):
        media = entry.media_content

        if media:
            for item in media:
                url = item.get("url")

                if url:
                    return url

    # 2. media_thumbnail
    if hasattr(entry, "media_thumbnail"):
        media = entry.media_thumbnail

        if media:
            for item in media:
                url = item.get("url")

                if url:
                    return url

    # 3. enclosures
    if hasattr(entry, "enclosures"):
        for item in entry.enclosures:
            url = item.get("href") or item.get("url")

            if url:
                return url

    # 4. image field
    if hasattr(entry, "image"):
        image = entry.image

        if isinstance(image, dict):
            url = image.get("href") or image.get("url")

            if url:
                return url

    # 5. summary HTML
    summary = entry.get("summary", "")

    if summary:
        match = re.search(
            r'<img[^>]+(?:src|data-src)=["\']([^"\']+)["\']',
            summary,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

    # 6. content HTML
    if hasattr(entry, "content"):
        for content in entry.content:
            html = content.get("value", "")

            match = re.search(
                r'<img[^>]+(?:src|data-src)=["\']([^"\']+)["\']',
                html,
                re.IGNORECASE
            )

            if match:
                return match.group(1)

    # 7. Look for image URLs anywhere in the entry
    for key, value in entry.items():

        if isinstance(value, str):

            match = re.search(
                r'https?://[^"\']+\.(?:jpg|jpeg|png|webp)(?:\?[^"\']*)?',
                value,
                re.IGNORECASE
            )

            if match:
                return match.group(0)

    # No image found
    return None


NEWS_FEEDS = {
    "BBC": {
        "url": "https://feeds.bbci.co.uk/news/rss.xml",
        "category": "general"
    },
    "BBC World": {
        "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "category": "world"
    },
    "BBC Technology": {
        "url": "https://feeds.bbci.co.uk/news/technology/rss.xml",
        "category": "technology"
    },
    "BBC Science": {
        "url": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
        "category": "science"
    },
    "BBC Sport": {
        "url": "https://feeds.bbci.co.uk/sport/rss.xml",
        "category": "sports"
    },
    "NPR": {
        "url": "https://feeds.npr.org/1001/rss.xml",
        "category": "general"
    },
    "NPR World": {
        "url": "https://feeds.npr.org/1004/rss.xml",
        "category": "world"
    },
    "NPR Business": {
        "url": "https://feeds.npr.org/1006/rss.xml",
        "category": "business"
    },
    "NPR Technology": {
        "url": "https://feeds.npr.org/1019/rss.xml",
        "category": "technology"
    },
    "NPR Science": {
        "url": "https://feeds.npr.org/1007/rss.xml",
        "category": "science"
    },
    "NPR Sports": {
        "url": "https://feeds.npr.org/1055/rss.xml",
        "category": "sports"
    },
    "Ars Technica": {
        "url": "https://feeds.arstechnica.com/arstechnica/index",
        "category": "technology"
    },
    "CNBC": {
        "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "category": "business"
    },
}


def get_news(category=None, source=None, limit=50):
    articles = []
    seen_links = set()

    for source_name, feed_info in NEWS_FEEDS.items():

        # Filter by source
        if source and source.lower() != source_name.lower():
            continue

        # Filter by category
        if category and category.lower() != feed_info["category"].lower():
            continue

        # Parse RSS feed
        feed = feedparser.parse(feed_info["url"])

        # Get up to 10 articles from each source
        for entry in feed.entries[:10]:

            link = entry.get("link")

            # Skip articles without links
            if not link:
                continue

            # Skip duplicate articles
            if link in seen_links:
                continue

            seen_links.add(link)

            # Get publication date
            published = entry.get("published")

            try:
                published_date = parsedate_to_datetime(published)
                published_timestamp = published_date.timestamp()

            except (TypeError, ValueError):
                published_timestamp = 0

            # Build article
            article = {
                "source": source_name,
                "category": feed_info["category"],
                "title": entry.get("title"),
                "link": link,
                "published": published,
                "summary": entry.get("summary"),
                "_timestamp": published_timestamp,
                "image": get_image(entry)
            }

            articles.append(article)

            # Save article to database
            save_article(article)

    # Sort newest first
    articles.sort(
        key=lambda article: article["_timestamp"],
        reverse=True
    )

    # Return requested number of articles
    return articles[:limit]