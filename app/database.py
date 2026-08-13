import sqlite3


DATABASE = "news.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            link TEXT UNIQUE NOT NULL,
            published TEXT,
            summary TEXT,
            image TEXT,
            published_timestamp REAL
        )
    """)

    connection.commit()
    connection.close()


def save_article(article):
    connection = get_connection()

    connection.execute("""
        INSERT OR IGNORE INTO articles (
            source,
            category,
            title,
            link,
            published,
            summary,
            image,
            published_timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        article["source"],
        article["category"],
        article["title"],
        article["link"],
        article["published"],
        article["summary"],
        article["image"],
        article["_timestamp"]
    ))

    connection.commit()
    connection.close()


def get_articles(category=None, source=None, limit=50):
    connection = get_connection()

    query = """
        SELECT
            source,
            category,
            title,
            link,
            published,
            summary,
            image
        FROM articles
    """

    conditions = []
    parameters = []

    if category:
        conditions.append("category = ?")
        parameters.append(category)

    if source:
        conditions.append("source = ?")
        parameters.append(source)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += """
        ORDER BY published_timestamp DESC
        LIMIT ?
    """

    parameters.append(limit)

    rows = connection.execute(query, parameters).fetchall()

    connection.close()

    return [dict(row) for row in rows]