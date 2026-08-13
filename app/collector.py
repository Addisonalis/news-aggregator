from app.news import get_news
from app.database import initialize_database, save_article


def collect_news():
    print("Collecting news...")

    initialize_database()

    articles = get_news(limit=100)

    saved = 0

    for article in articles:
        try:
            save_article(article)
            saved += 1
        except Exception as e:
            print(f"Error saving article: {e}")

    print(f"Collected {len(articles)} articles.")
    print(f"Saved {saved} articles to database.")


if __name__ == "__main__":
    collect_news()