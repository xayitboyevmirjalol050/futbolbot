import os
from dotenv import load_dotenv

load_dotenv()

# ─── ASOSIY TOKENLAR ─────────────────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "")          # @kanalingsiz yoki -100xxxxxxxxx
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

# ─── API KALITLAR ─────────────────────────────────────────────────────────────
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "")   # football-data.org
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")           # claude tarjima uchun

# ─── YANGILIKLAR MANBALAR (RSS) ───────────────────────────────────────────────
NEWS_FEEDS = [
    {"name": "BBC Sport Football", "url": "https://feeds.bbci.co.uk/sport/football/rss.xml"},
    {"name": "Goal.com",           "url": "https://www.goal.com/feeds/en/news"},
    {"name": "UEFA",               "url": "https://www.uefa.com/rssfeed/"},
    {"name": "Sky Sports Football","url": "https://www.skysports.com/rss/12040"},
]

# ─── LIGALAR (football-data.org ID lari) ─────────────────────────────────────
LEAGUES = {
    "PL":  {"name": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League",    "id": 2021},
    "PD":  {"name": "🇪🇸 La Liga",              "id": 2014},
    "SA":  {"name": "🇮🇹 Serie A",              "id": 2019},
    "BL1": {"name": "🇩🇪 Bundesliga",           "id": 2002},
    "FL1": {"name": "🇫🇷 Ligue 1",             "id": 2015},
    "CL":  {"name": "🏆 Champions League",      "id": 2001},
    "EL":  {"name": "🥈 Europa League",         "id": 2146},
}

# ─── JADVAL ───────────────────────────────────────────────────────────────────
NEWS_INTERVAL_MINUTES = 60        # yangiliklar qanchalik tez tekshirilsin
RESULTS_CHECK_MINUTES = 15        # natijalar qanchalik tez tekshirilsin

# ─── MA'LUMOTLAR BAZASI ───────────────────────────────────────────────────────
DATABASE_URL = "football_bot.db"
