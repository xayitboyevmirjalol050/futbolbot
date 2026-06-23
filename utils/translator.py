import anthropic
from config import ANTHROPIC_API_KEY
import asyncio
import re

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def clean_text(text: str) -> str:
    text = text.replace("||", "")
    text = text.replace("**", "")
    text = text.replace("__", "")
    text = text.replace("~~", "")
    text = text.replace("`", "")
    text = text.replace("•", "-")
    text = text.replace("<b>", "").replace("</b>", "")
    text = text.replace("<i>", "").replace("</i>", "")
    text = text.replace("<u>", "").replace("</u>", "")
    return text.strip()


async def translate_and_format_news(title: str, summary: str, source: str) -> str:
    prompt = f"""Quyidagi futbol yangiligini o'zbek tiliga tarjima qilib, Telegram kanal uchun post yoz.

Sarlavha: {title}
Mazmun: {summary}

Qoidalar:
- Faqat o'zbek tilida yoz
- Emoji ishlat
- 3-5 gap, qisqa va aniq
- Manba, link, hashtag YOZMA
- Hech qanday format belgisi ishlatma

Post:"""

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
    )
    return clean_text(response.content[0].text)


async def translate_and_format_result(
    home_team: str, away_team: str,
    home_score: int, away_score: int,
    league_name: str, match_date: str,
    scorers: list = None
) -> str:
    scorers_text = ""
    if scorers:
        scorers_text = f"Gollar: {', '.join(scorers)}"

    prompt = f"""Futbol o'yini natijasi uchun Telegram post yoz. O'zbek tilida.

Liga: {league_name}
{home_team} {home_score} - {away_score} {away_team}
Sana: {match_date}
{scorers_text}

Qoidalar:
- O'zbek tilida, emotsional
- Emoji ishlat
- 3-5 qator
- Manba, link, hashtag YOZMA
- Hech qanday format belgisi ishlatma

Post:"""

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
    )
    return clean_text(response.content[0].text)
