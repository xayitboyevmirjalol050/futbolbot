import logging
import asyncio
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import CHANNEL_ID, NEWS_INTERVAL_MINUTES, RESULTS_CHECK_MINUTES
from database import is_news_posted, mark_news_posted, is_result_posted, mark_result_posted
from utils.news_fetcher import fetch_all_news
from utils.results_fetcher import fetch_finished_matches
from utils.translator import translate_and_format_news, translate_and_format_result

logger = logging.getLogger(__name__)


async def post_news_job(bot: Bot):
    """Yangi yangiliklar tekshirish va kanalga yuborish"""
    logger.info("Yangiliklar tekshirilmoqda...")
    try:
        news_list = await fetch_all_news()
        posted = 0
        for news in news_list:
            if await is_news_posted(news["url"]):
                continue
            try:
                post_text = await translate_and_format_news(
                    title=news["title"],
                    summary=news["summary"],
                    source=news["source"]
                )
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=post_text,
                    parse_mode="HTML"
                )
                await mark_news_posted(news["url"], news["title"])
                posted += 1
                logger.info(f"Yangilik joylandi: {news['title'][:60]}")
                await asyncio.sleep(3)  # Flood limitdan saqlash
            except Exception as e:
                logger.error(f"Yangilik joylashda xatolik: {e}")
                await asyncio.sleep(2)

        if posted:
            logger.info(f"{posted} ta yangilik joylandi")
        else:
            logger.info("Yangi yangilik yo'q")
    except Exception as e:
        logger.error(f"Yangiliklar jobida xatolik: {e}")


async def post_results_job(bot: Bot):
    """Tugagan o'yinlar natijalarini tekshirish va joylash"""
    logger.info("O'yin natijalari tekshirilmoqda...")
    try:
        matches = await fetch_finished_matches()
        posted = 0
        for match in matches:
            if await is_result_posted(match["id"]):
                continue
            try:
                post_text = await translate_and_format_result(
                    home_team=match["home_team"],
                    away_team=match["away_team"],
                    home_score=match["home_score"],
                    away_score=match["away_score"],
                    league_name=match["league_name"],
                    match_date=match["date"],
                    scorers=match["scorers"]
                )
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=post_text,
                    parse_mode="HTML"
                )
                await mark_result_posted(match["id"])
                posted += 1
                logger.info(f"Natija joylandi: {match['home_team']} vs {match['away_team']}")
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"Natija joylashda xatolik: {e}")
                await asyncio.sleep(2)

        if posted:
            logger.info(f"{posted} ta natija joylandi")
        else:
            logger.info("Yangi natija yo'q")
    except Exception as e:
        logger.error(f"Natijalar jobida xatolik: {e}")


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    """Schedulerni sozlash va ishga tushirish"""
    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")

    # Yangiliklar: har N daqiqada
    scheduler.add_job(
        post_news_job,
        trigger="interval",
        minutes=NEWS_INTERVAL_MINUTES,
        args=[bot],
        id="news_job",
        name="Yangiliklar joylash"
    )

    # Natijalar: har 15 daqiqada
    scheduler.add_job(
        post_results_job,
        trigger="interval",
        minutes=RESULTS_CHECK_MINUTES,
        args=[bot],
        id="results_job",
        name="Natijalar joylash"
    )

    return scheduler
