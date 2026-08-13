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

    return None


NEWS_FEEDS = {

    # =========================
    # GENERAL
    # =========================

    "BBC": {
        "url": "https://feeds.bbci.co.uk/news/rss.xml",
        "category": "general"
    },

    "NPR": {
        "url": "https://feeds.npr.org/1001/rss.xml",
        "category": "general"
    },

    "CBS News": {
        "url": "https://www.cbsnews.com/latest/rss/main",
        "category": "general"
    },

    "NBC News": {
        "url": "https://feeds.nbcnews.com/nbcnews/public/news",
        "category": "general"
    },

    "ABC News": {
        "url": "https://abcnews.com/abcnews/topstories",
        "category": "general"
    },

    "USA Today": {
        "url": "https://rssfeeds.usatoday.com/usatoday-NewsTopStories",
        "category": "general"
    },

    "The Hill": {
        "url": "https://thehill.com/feed/",
        "category": "general"
    },

    # =========================
    # WORLD
    # =========================

    "BBC World": {
        "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "category": "world"
    },

    "NPR World": {
        "url": "https://feeds.npr.org/1004/rss.xml",
        "category": "world"
    },

    "Al Jazeera": {
        "url": "https://www.aljazeera.com/xml/rss/all.xml",
        "category": "world"
    },

    "DW World": {
        "url": "https://rss.dw.com/rdf/rss-en-all",
        "category": "world"
    },

    "Guardian World": {
        "url": "https://www.theguardian.com/world/rss",
        "category": "world"
    },

    "France 24": {
        "url": "https://www.france24.com/en/rss",
        "category": "world"
    },

    # =========================
    # BUSINESS
    # =========================

    "NPR Business": {
        "url": "https://feeds.npr.org/1006/rss.xml",
        "category": "business"
    },

    "CNBC": {
        "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "category": "business"
    },

    "MarketWatch": {
        "url": "https://feeds.marketwatch.com/marketwatch/topstories/",
        "category": "business"
    },

    "Forbes": {
        "url": "https://www.forbes.com/real-time/feed2/",
        "category": "business"
    },

    "Fortune": {
        "url": "https://fortune.com/feed/",
        "category": "business"
    },

    "Business Insider": {
        "url": "https://feeds.businessinsider.com/custom/all",
        "category": "business"
    },

    # =========================
    # TECHNOLOGY
    # =========================

    "BBC Technology": {
        "url": "https://feeds.bbci.co.uk/news/technology/rss.xml",
        "category": "technology"
    },

    "NPR Technology": {
        "url": "https://feeds.npr.org/1019/rss.xml",
        "category": "technology"
    },

    "Ars Technica": {
        "url": "https://feeds.arstechnica.com/arstechnica/index",
        "category": "technology"
    },

    "TechCrunch": {
        "url": "https://techcrunch.com/feed/",
        "category": "technology"
    },

    "The Verge": {
        "url": "https://www.theverge.com/rss/index.xml",
        "category": "technology"
    },

    "Wired": {
        "url": "https://www.wired.com/feed/rss",
        "category": "technology"
    },

    "Engadget": {
        "url": "https://www.engadget.com/rss.xml",
        "category": "technology"
    },

    "VentureBeat": {
        "url": "https://venturebeat.com/feed/",
        "category": "technology"
    },

    "CNET": {
        "url": "https://www.cnet.com/rss/news/",
        "category": "technology"
    },

    # =========================
    # SCIENCE
    # =========================

    "BBC Science": {
        "url": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
        "category": "science"
    },

    "NPR Science": {
        "url": "https://feeds.npr.org/1007/rss.xml",
        "category": "science"
    },

    "NASA": {
        "url": "https://www.nasa.gov/rss/dyn/breaking_news.rss",
        "category": "science"
    },

    "ScienceDaily": {
        "url": "https://www.sciencedaily.com/rss/all.xml",
        "category": "science"
    },

    "Phys.org": {
        "url": "https://phys.org/rss-feed/",
        "category": "science"
    },

    "New Scientist": {
        "url": "https://www.newscientist.com/feed/home/",
        "category": "science"
    },

    "Scientific American": {
        "url": "http://rss.sciam.com/ScientificAmerican-Global",
        "category": "science"
    },

    # =========================
    # SPORTS
    # =========================

    "BBC Sport": {
        "url": "https://feeds.bbci.co.uk/sport/rss.xml",
        "category": "sports"
    },

    "NPR Sports": {
        "url": "https://feeds.npr.org/1055/rss.xml",
        "category": "sports"
    },

    "ESPN": {
        "url": "https://www.espn.com/espn/rss/news",
        "category": "sports"
    },

    "CBS Sports": {
        "url": "https://www.cbssports.com/rss/headlines/",
        "category": "sports"
    },

    "NBC Sports": {
        "url": "https://www.nbcsports.com/feed",
        "category": "sports"
    },

    # =========================
    # ENTERTAINMENT
    # =========================

    "Variety": {
        "url": "https://variety.com/feed/",
        "category": "entertainment"
    },

    "Rolling Stone": {
        "url": "https://www.rollingstone.com/feed/",
        "category": "entertainment"
    },

    "Hollywood Reporter": {
        "url": "https://www.hollywoodreporter.com/feed/",
        "category": "entertainment"
    },

    "Deadline": {
        "url": "https://deadline.com/feed/",
        "category": "entertainment"
    },
}


def clean_summary(raw_summary):
    """
    Remove HTML and prevent RSS feeds from displaying
    extremely long full-article descriptions.
    """

    if not raw_summary:
        return ""

    # Remove HTML tags
    summary = re.sub(r"<[^>]+>", "", raw_summary)

    # Decode common HTML entities
    summary = (
        summary
        .replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
    )

    # Clean whitespace
    summary = re.sub(r"\s+", " ", summary).strip()

    # Limit summary length
    if len(summary) > 300:
        summary = summary[:300].rsplit(" ", 1)[0] + "..."

    return summary


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

        try:

            feed = feedparser.parse(
                feed_info["url"],
                request_headers={
                    "User-Agent": "Mozilla/5.0 NewsAggregator/1.0"
                }
            )

            if not feed.entries:
                print(f"No articles found: {source_name}")
                continue

        except Exception as error:

            print(f"Feed failed: {source_name} - {error}")
            continue

        for entry in feed.entries[:15]:

            link = entry.get("link")

            if not link or link in seen_links:
                continue

            seen_links.add(link)

            # Publication date
            published = entry.get("published")

            try:

                published_date = parsedate_to_datetime(published)
                published_timestamp = published_date.timestamp()

            except (TypeError, ValueError):

                published_timestamp = 0

            # Clean article summary
            raw_summary = entry.get("summary", "")
            summary = clean_summary(raw_summary)

            # Build article
            article = {
                "source": source_name,
                "category": feed_info["category"],
                "title": entry.get("title"),
                "link": link,
                "published": published,
                "summary": summary,
                "_timestamp": published_timestamp,
                "image": get_image(entry)
            }

            articles.append(article)

            # Save to database
            try:

                save_article(article)

            except Exception as error:

                print(
                    f"Database error for {source_name}: {error}"
                )

    # Newest articles first
    articles.sort(
        key=lambda article: article["_timestamp"],
        reverse=True
    )

    return articles[:limit]