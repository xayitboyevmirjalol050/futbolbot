# ⚽ Futbol Yangiliklar Bot

Avtomatik ravishda futbol yangiliklari va o'yin natijalarini o'zbek tiliga tarjima qilib kanalga joylaydi.

## 📁 Fayl tuzilmasi

```
football_bot/
├── bot.py                  ← Ishga tushirish
├── config.py               ← Sozlamalar
├── database.py             ← Ma'lumotlar bazasi
├── keyboards.py            ← Tugmalar
├── requirements.txt        ← Kutubxonalar
├── .env.example            ← .env namunasi
└── handlers/
│   ├── admin.py            ← Admin panel
│   └── user.py             ← Foydalanuvchilar
└── utils/
    ├── translator.py       ← Claude AI tarjima
    ├── news_fetcher.py     ← RSS yangiliklar
    ├── results_fetcher.py  ← football-data.org natijalar
    └── scheduler.py        ← Avtomatik joylash
```

---

## ⚙️ O'rnatish (qadam-baqadam)

### 1. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 2. API kalitlarni olish

**Bot token:**
- Telegramda `@BotFather` → `/newbot` → token nusxalang

**Kanal ID:**
- Botni kanalga **admin** qilib qo'shing (post yuborish huquqi bilan)
- `@kanalingiz` yoki `-100xxxxxxxxx` formatida

**Admin ID:**
- `@userinfobot` ga `/start` yuboring

**Football-data.org API (BEPUL):**
- https://www.football-data.org/client/register
- Ro'yxatdan o'ting → email keladi → API key oling

**Anthropic API (Claude tarjima uchun):**
- https://console.anthropic.com
- API Keys → Create Key

### 3. .env fayl yarating
```bash
cp .env.example .env
```
`.env` faylini oching va kalitlarni to'ldiring.

### 4. Botni ishga tushiring
```bash
python bot.py
```

---

## 🛡️ Admin Panel (`/admin`)

| Tugma | Funksiya |
|-------|----------|
| 👥 Obunachilar | Ro'yxat va sahifalash |
| 📊 Statistika | Jami, faol, ban soni |
| 📢 E'lon yuborish | Barcha obunachilarga xabar |
| 📋 E'lonlar | So'nggi e'lonlar tarixi |
| ⚡ Yangilik qo'lda joylash | Sarlavha + mazmun → tarjima → kanal |
| ⚽ Natija qo'lda joylash | Natija → tarjima → kanal |

### Maxsus komandalar (admin uchun)
```
/fetch_news     — hoziroq yangiliklar tekshirish
/fetch_results  — hoziroq natijalar tekshirish
```

---

## 🤖 Avtomatik joylash jadvali

| Vazifa | Interval |
|--------|----------|
| Yangiliklar (RSS) | Har 60 daqiqada |
| O'yin natijalari | Har 15 daqiqada |

---

## 📡 Yangilik manbalari

- BBC Sport Football
- Goal.com
- UEFA
- Sky Sports Football

---

## ⚽ Qo'llab-quvvatlanadigan ligalar

- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League
- 🇪🇸 La Liga
- 🇮🇹 Serie A
- 🇩🇪 Bundesliga
- 🇫🇷 Ligue 1
- 🏆 Champions League
- 🥈 Europa League
