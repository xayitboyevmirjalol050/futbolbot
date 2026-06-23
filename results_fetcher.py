import logging
import aiohttp
from datetime import datetime, timedelta
from config import FOOTBALL_DATA_API_KEY, LEAGUES

logger = logging.getLogger(__name__)

BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": FOOTBALL_DATA_API_KEY}


async def fetch_finished_matches() -> list:
    """
    Bugun va kecha yakunlangan o'yinlarni olish.
    Faqat hali post qilinmaganlar keyinroq filtrlanadi.
    """
    results = []
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)
    date_from = yesterday.isoformat()
    date_to = today.isoformat()

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        for code, league in LEAGUES.items():
            url = f"{BASE_URL}/competitions/{code}/matches"
            params = {
                "dateFrom": date_from,
                "dateTo": date_to,
                "status": "FINISHED"
            }
            try:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for match in data.get("matches", []):
                            score = match.get("score", {})
                            full = score.get("fullTime", {})
                            home_score = full.get("home")
                            away_score = full.get("away")
                            if home_score is None or away_score is None:
                                continue

                            # Golchilar
                            scorers = []
                            for goal in match.get("goals", []):
                                scorer = goal.get("scorer", {}).get("name", "")
                                team = goal.get("team", {}).get("shortName", "")
                                minute = goal.get("minute", "")
                                if scorer:
                                    scorers.append(f"{scorer} ({team}, {minute}')")

                            match_date = match.get("utcDate", "")[:10]
                            results.append({
                                "id": match["id"],
                                "league_name": league["name"],
                                "home_team": match["homeTeam"].get("shortName") or match["homeTeam"]["name"],
                                "away_team": match["awayTeam"].get("shortName") or match["awayTeam"]["name"],
                                "home_score": home_score,
                                "away_score": away_score,
                                "date": match_date,
                                "scorers": scorers
                            })
                    elif resp.status == 429:
                        logger.warning("API limit oshib ketdi, keyingi tekshirishga o'tiladi")
                        break
                    else:
                        logger.warning(f"{code} ligasi uchun xatolik: {resp.status}")
            except Exception as e:
                logger.error(f"{code} ligasi fetch xatosi: {e}")

    logger.info(f"Jami {len(results)} ta tugagan o'yin topildi")
    return results
