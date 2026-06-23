import logging
import feedparser
import aiohttp
from bs4 import BeautifulSoup
from config import NEWS_FEEDS

logger = logging.getLogger(__name__)


async def fetch_feed(session: aiohttp.ClientSession, feed: dict) -> list:
    """Bitta RSS manbadan yangiliklar olish"""
    try:
        async with session.get(feed["url"], timeout=aiohttp.ClientTimeout(total=15)) as resp:
            content = await resp.text()
        parsed = feedparser.parse(content)
        items = []
        for entry in parsed.entries[:5]:  # Har manbadan max 5 ta
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            summary = entry.get("summary", "") or entry.get("description", "")
            # HTML teglarini tozalash
            if summary:
                soup = BeautifulSoup(summary, "lxml")
                summary = soup.get_text(separator=" ").strip()[:600]
            if title and link:
                items.append({
                    "title": title,
                    "url": link,
                    "summary": summary,
                    "source": feed["name"]
                })
        return items
    except Exception as e:
        logger.warning(f"RSS xatosi ({feed['name']}): {e}")
        return []


async def fetch_all_news() -> list:
    """Barcha manbalardan yangiliklar olish"""
    all_news = []
    async with aiohttp.ClientSession(headers={
        "User-Agent": "Mozilla/5.0 (compatible; FootballBot/1.0)"
    }) as session:
        for feed in NEWS_FEEDS:
            items = await fetch_feed(session, feed)
            all_news.extend(items)
    # Takrorlarni olib tashlash (URL bo'yicha)
    seen = set()
    unique = []
    for item in all_news:
        if item["url"] not in seen:
            seen.add(item["url"])
            unique.append(item)
    logger.info(f"Jami {len(unique)} ta yangilik topildi")
    return unique
