from apscheduler.schedulers.background import BackgroundScheduler

from app.collector import collect_news


scheduler = BackgroundScheduler()


def start_scheduler():
    scheduler.add_job(
        collect_news,
        "interval",
        minutes=10,
        id="news_collection",
        replace_existing=True
    )

    scheduler.start()
    print("News scheduler started. Collecting every 10 minutes.")