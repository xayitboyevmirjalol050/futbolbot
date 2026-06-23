import anthropic
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


async def translate_and_format_news(title: str, summary: str, source: str) -> str:
    """
    Yangilikni o'zbekchaga tarjima qilib, chiroyli Telegram post qiladi.
    Manba ko'rsatilmaydi.
    """
    prompt = f"""Quyidagi futbol yangiligini o'zbek tiliga tarjima qilib, Telegram kanal uchun chiroyli post yoz.

Sarlavha: {title}
Mazmun: {summary}

Qoidalar:
- Faqat o'zbek tilida yoz
- Post sarlavhasi katta va emotsional bo'lsin (emoji bilan)
- 3-5 gap, qisqa va aniq
- Kerakli joyda emoji ishlat (⚽🔥🏆💥👑 va h.k.)
- Manba, link, hashtag YOZMA
- Faqat postni yoz, boshqa hech narsa qo'shma

Post:"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


async def translate_and_format_result(
    home_team: str, away_team: str,
    home_score: int, away_score: int,
    league_name: str, match_date: str,
    scorers: list = None
) -> str:
    """
    O'yin natijasini o'zbekchaga tarjima qilib, chiroyli post qiladi.
    """
    scorers_text = ""
    if scorers:
        scorers_text = f"Gollar: {', '.join(scorers)}"

    prompt = f"""Quyidagi futbol o'yini natijasi uchun Telegram kanal posti yoz. O'zbek tilida.

Liga: {league_name}
{home_team} {home_score} - {away_score} {away_team}
Sana: {match_date}
{scorers_text}

Qoidalar:
- O'zbek tilida, chiroyli, emotsional
- Natija yaxshi ko'zga tashlansin (katta raqamlar yoki emoji)
- Kim g'olib, mag'lub yoki durrang bo'lganini ayt
- Golchilar bo'lsa qayt
- 3-5 qator
- Manba, link, hashtag YOZMA
- Faqat postni yoz

Post:"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()
