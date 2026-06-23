import aiosqlite
from config import DATABASE_URL


async def init_db():
    async with aiosqlite.connect(DATABASE_URL) as db:
        # Foydalanuvchilar
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                full_name TEXT,
                is_banned INTEGER DEFAULT 0,
                joined_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Chop etilgan yangiliklar (takrorlanmaslik uchun)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS posted_news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT,
                posted_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Chop etilgan natijalar
        await db.execute("""
            CREATE TABLE IF NOT EXISTS posted_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER UNIQUE NOT NULL,
                posted_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # E'lonlar
        await db.execute("""
            CREATE TABLE IF NOT EXISTS broadcasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                sent_count INTEGER DEFAULT 0,
                sent_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


# ─── FOYDALANUVCHILAR ─────────────────────────────────────────────────────────

async def add_user(user_id: int, username: str, full_name: str):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("""
            INSERT INTO users (user_id, username, full_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username,
                full_name=excluded.full_name
        """, (user_id, username or "", full_name or ""))
        await db.commit()


async def get_users_count():
    async with aiosqlite.connect(DATABASE_URL) as db:
        async with db.execute("SELECT COUNT(*) FROM users WHERE is_banned=0") as c:
            active = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM users") as c:
            total = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM users WHERE is_banned=1") as c:
            banned = (await c.fetchone())[0]
    return {"total": total, "active": active, "banned": banned}


async def get_all_active_users():
    async with aiosqlite.connect(DATABASE_URL) as db:
        async with db.execute("SELECT user_id FROM users WHERE is_banned=0") as c:
            rows = await c.fetchall()
    return [r[0] for r in rows]


async def ban_user(user_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("UPDATE users SET is_banned=1 WHERE user_id=?", (user_id,))
        await db.commit()


async def unban_user(user_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("UPDATE users SET is_banned=0 WHERE user_id=?", (user_id,))
        await db.commit()


async def get_all_users(page: int = 1, per_page: int = 10):
    offset = (page - 1) * per_page
    async with aiosqlite.connect(DATABASE_URL) as db:
        async with db.execute(
            "SELECT user_id, username, full_name, is_banned, joined_at FROM users ORDER BY joined_at DESC LIMIT ? OFFSET ?",
            (per_page, offset)
        ) as c:
            rows = await c.fetchall()
            cols = ["user_id", "username", "full_name", "is_banned", "joined_at"]
            return [dict(zip(cols, r)) for r in rows]


# ─── YANGILIKLAR ─────────────────────────────────────────────────────────────

async def is_news_posted(url: str) -> bool:
    async with aiosqlite.connect(DATABASE_URL) as db:
        async with db.execute("SELECT id FROM posted_news WHERE url=?", (url,)) as c:
            return (await c.fetchone()) is not None


async def mark_news_posted(url: str, title: str):
    async with aiosqlite.connect(DATABASE_URL) as db:
        try:
            await db.execute("INSERT INTO posted_news (url, title) VALUES (?, ?)", (url, title))
            await db.commit()
        except Exception:
            pass


# ─── NATIJALAR ───────────────────────────────────────────────────────────────

async def is_result_posted(match_id: int) -> bool:
    async with aiosqlite.connect(DATABASE_URL) as db:
        async with db.execute("SELECT id FROM posted_results WHERE match_id=?", (match_id,)) as c:
            return (await c.fetchone()) is not None


async def mark_result_posted(match_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        try:
            await db.execute("INSERT INTO posted_results (match_id) VALUES (?)", (match_id,))
            await db.commit()
        except Exception:
            pass


# ─── E'LONLAR ─────────────────────────────────────────────────────────────────

async def save_broadcast(text: str, sent_count: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("INSERT INTO broadcasts (text, sent_count) VALUES (?, ?)", (text, sent_count))
        await db.commit()


async def get_recent_broadcasts(limit: int = 5):
    async with aiosqlite.connect(DATABASE_URL) as db:
        async with db.execute(
            "SELECT text, sent_count, sent_at FROM broadcasts ORDER BY sent_at DESC LIMIT ?", (limit,)
        ) as c:
            rows = await c.fetchall()
            return [{"text": r[0], "sent_count": r[1], "sent_at": r[2]} for r in rows]
