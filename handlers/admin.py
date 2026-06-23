import asyncio
import logging
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_IDS, CHANNEL_ID
from keyboards import admin_main_menu, back_btn, confirm_broadcast_kb, users_nav
import database as db
from utils.scheduler import post_news_job, post_results_job
from utils.translator import translate_and_format_news, translate_and_format_result

logger = logging.getLogger(__name__)
router = Router()


def is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS


# ─── FSM ─────────────────────────────────────────────────────────────────────

class BroadcastFSM(StatesGroup):
    text   = State()
    confirm = State()

class ManualNewsFSM(StatesGroup):
    title   = State()
    summary = State()

class ManualResultFSM(StatesGroup):
    data = State()


# ─── BOSH PANEL ──────────────────────────────────────────────────────────────

@router.message(Command("admin"))
async def cmd_admin(msg: Message):
    if not is_admin(msg.from_user.id):
        return await msg.answer("⛔ Ruxsat yo'q.")
    stats = await db.get_users_count()
    await msg.answer(
        f"🛡️ <b>Admin Panel</b>\n\n"
        f"👥 Obunachilar: <b>{stats['total']}</b>  |  Faol: <b>{stats['active']}</b>  |  Ban: <b>{stats['banned']}</b>",
        reply_markup=admin_main_menu(), parse_mode="HTML"
    )


@router.callback_query(F.data == "admin_back")
async def cb_back(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id): return await call.answer()
    await state.clear()
    stats = await db.get_users_count()
    await call.message.edit_text(
        f"🛡️ <b>Admin Panel</b>\n\n"
        f"👥 Obunachilar: <b>{stats['total']}</b>  |  Faol: <b>{stats['active']}</b>  |  Ban: <b>{stats['banned']}</b>",
        reply_markup=admin_main_menu(), parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data == "close")
async def cb_close(call: CallbackQuery):
    await call.message.delete()
    await call.answer()


# ─── STATISTIKA ──────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin_stats")
async def cb_stats(call: CallbackQuery):
    if not is_admin(call.from_user.id): return await call.answer()
    stats = await db.get_users_count()
    broadcasts = await db.get_recent_broadcasts(limit=3)
    total_reach = sum(b["sent_count"] for b in broadcasts)
    await call.message.edit_text(
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Jami obunachilar: <b>{stats['total']}</b>\n"
        f"✅ Faol: <b>{stats['active']}</b>\n"
        f"🚫 Bloklangan: <b>{stats['banned']}</b>\n\n"
        f"📢 So'nggi {len(broadcasts)} ta e'lon — {total_reach} ta yetib bordi",
        reply_markup=back_btn(), parse_mode="HTML"
    )
    await call.answer()


# ─── OBUNACHILAR ─────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin_users")
async def cb_users(call: CallbackQuery):
    if not is_admin(call.from_user.id): return await call.answer()
    await show_users_page(call, 1)


@router.callback_query(F.data.startswith("users_page_"))
async def cb_users_page(call: CallbackQuery):
    if not is_admin(call.from_user.id): return await call.answer()
    page = int(call.data.split("_")[-1])
    await show_users_page(call, page)


async def show_users_page(call: CallbackQuery, page: int):
    per_page = 10
    stats = await db.get_users_count()
    total_pages = max(1, (stats["total"] + per_page - 1) // per_page)
    users = await db.get_all_users(page=page, per_page=per_page)

    lines = [f"👥 <b>Obunachilar</b> ({stats['total']} ta) — sahifa {page}/{total_pages}\n"]
    for u in users:
        icon = "🚫" if u["is_banned"] else "✅"
        name = u["full_name"] or "Nomsiz"
        uname = f"@{u['username']}" if u["username"] else "—"
        lines.append(f"{icon} {name} | {uname} | <code>{u['user_id']}</code>")

    await call.message.edit_text(
        "\n".join(lines),
        reply_markup=users_nav(page, total_pages),
        parse_mode="HTML"
    )
    await call.answer()


# ─── E'LON YUBORISH ──────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin_broadcast")
async def cb_broadcast_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id): return await call.answer()
    await state.set_state(BroadcastFSM.text)
    await call.message.edit_text(
        "📢 <b>E'lon matni</b>\n\nBarcha obunachilarga yuboriladigan xabarni yozing.\n"
        "HTML formatlash qo'llaniladi. Bekor qilish: /cancel",
        reply_markup=None, parse_mode="HTML"
    )
    await call.answer()


@router.message(BroadcastFSM.text)
async def fsm_broadcast_text(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id): return
    if msg.text == "/cancel":
        await state.clear()
        return await msg.answer("❌ Bekor qilindi.")
    await state.update_data(text=msg.text)
    await state.set_state(BroadcastFSM.confirm)
    stats = await db.get_users_count()
    await msg.answer(
        f"📋 <b>Ko'rinish:</b>\n\n{msg.text}\n\n"
        f"━━━━━━━━━━━━\n👥 {stats['active']} ta obunachiga yuboriladi.",
        reply_markup=confirm_broadcast_kb(), parse_mode="HTML"
    )


@router.callback_query(F.data == "broadcast_no")
async def cb_broadcast_no(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("❌ E'lon bekor qilindi.", reply_markup=back_btn())
    await call.answer()


@router.callback_query(F.data == "broadcast_yes")
async def cb_broadcast_yes(call: CallbackQuery, state: FSMContext, bot: Bot):
    if not is_admin(call.from_user.id): return await call.answer()
    data = await state.get_data()
    text = data.get("text", "")
    await state.clear()

    users = await db.get_all_active_users()
    await call.message.edit_text(f"⏳ Yuborilmoqda... (0/{len(users)})")
    await call.answer()

    sent = failed = 0
    for i, uid in enumerate(users, 1):
        try:
            await bot.send_message(uid, text, parse_mode="HTML")
            sent += 1
        except Exception:
            failed += 1
        if i % 25 == 0:
            try:
                await call.message.edit_text(f"⏳ Yuborilmoqda... ({i}/{len(users)})")
            except Exception:
                pass
        await asyncio.sleep(0.04)

    await db.save_broadcast(text, sent)
    await call.message.edit_text(
        f"✅ <b>E'lon yuborildi!</b>\n\n📤 Yetdi: <b>{sent}</b>  ❌ Yetmadi: <b>{failed}</b>",
        reply_markup=back_btn(), parse_mode="HTML"
    )


# ─── E'LONLAR TARIXI ─────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin_broadcasts")
async def cb_broadcasts(call: CallbackQuery):
    if not is_admin(call.from_user.id): return await call.answer()
    items = await db.get_recent_broadcasts(limit=5)
    if not items:
        return await call.message.edit_text("📭 Hali e'lon yuborilmagan.", reply_markup=back_btn())
    lines = ["📋 <b>So'nggi e'lonlar:</b>\n"]
    for b in items:
        preview = b["text"][:80].replace("\n", " ")
        lines.append(f"📅 {b['sent_at'][:10]}  👥 {b['sent_count']} ta\n   {preview}…\n")
    await call.message.edit_text("\n".join(lines), reply_markup=back_btn(), parse_mode="HTML")
    await call.answer()


# ─── QO'LDA YANGILIK JOYLASH ─────────────────────────────────────────────────

@router.callback_query(F.data == "admin_manual_news")
async def cb_manual_news(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id): return await call.answer()
    await state.set_state(ManualNewsFSM.title)
    await call.message.edit_text(
        "⚡ <b>Qo'lda yangilik joylash</b>\n\nYangilik sarlavhasini yozing:",
        reply_markup=None, parse_mode="HTML"
    )
    await call.answer()


@router.message(ManualNewsFSM.title)
async def fsm_manual_news_title(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id): return
    await state.update_data(title=msg.text)
    await state.set_state(ManualNewsFSM.summary)
    await msg.answer("Qisqacha mazmunini yozing (yoki — deb yozing agar yo'q bo'lsa):")


@router.message(ManualNewsFSM.summary)
async def fsm_manual_news_summary(msg: Message, state: FSMContext, bot: Bot):
    if not is_admin(msg.from_user.id): return
    data = await state.get_data()
    await state.clear()
    summary = "" if msg.text == "—" else msg.text
    wait_msg = await msg.answer("⏳ Tarjima qilinmoqda...")
    try:
        post_text = await translate_and_format_news(data["title"], summary, "")
        await bot.send_message(CHANNEL_ID, post_text, parse_mode="HTML")
        await wait_msg.edit_text("✅ Yangilik kanalga joylandi!", reply_markup=back_btn())
    except Exception as e:
        await wait_msg.edit_text(f"❌ Xatolik: {e}", reply_markup=back_btn())


# ─── QO'LDA NATIJA JOYLASH ────────────────────────────────────────────────────

@router.callback_query(F.data == "admin_manual_result")
async def cb_manual_result(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id): return await call.answer()
    await state.set_state(ManualResultFSM.data)
    await call.message.edit_text(
        "⚽ <b>Qo'lda natija joylash</b>\n\n"
        "Quyidagi formatda yozing:\n\n"
        "<code>Liga nomi\nUy jamoasi - Mehmon jamoasi\n2 - 1\nGolchi1 (45'), Golchi2 (78')</code>\n\n"
        "Golchilar bo'lmasa — deb yozing.",
        reply_markup=None, parse_mode="HTML"
    )
    await call.answer()


@router.message(ManualResultFSM.data)
async def fsm_manual_result(msg: Message, state: FSMContext, bot: Bot):
    if not is_admin(msg.from_user.id): return
    await state.clear()
    lines = [l.strip() for l in msg.text.strip().split("\n") if l.strip()]
    try:
        league = lines[0]
        teams = lines[1].split("-")
        home_team = teams[0].strip()
        away_team = teams[1].strip()
        scores = lines[2].split("-")
        home_score = int(scores[0].strip())
        away_score = int(scores[1].strip())
        scorers_raw = lines[3] if len(lines) > 3 else ""
        scorers = [] if scorers_raw == "—" else [s.strip() for s in scorers_raw.split(",")]
    except Exception:
        return await msg.answer(
            "❌ Format noto'g'ri. Iltimos qayta urinib ko'ring.", reply_markup=back_btn()
        )

    wait_msg = await msg.answer("⏳ Tarjima qilinmoqda...")
    try:
        post_text = await translate_and_format_result(
            home_team=home_team, away_team=away_team,
            home_score=home_score, away_score=away_score,
            league_name=league, match_date="bugun", scorers=scorers
        )
        await bot.send_message(CHANNEL_ID, post_text, parse_mode="HTML")
        await wait_msg.edit_text("✅ Natija kanalga joylandi!", reply_markup=back_btn())
    except Exception as e:
        await wait_msg.edit_text(f"❌ Xatolik: {e}", reply_markup=back_btn())


# ─── SCHEDULER QO'LDA ISHGA TUSHIRISH ────────────────────────────────────────

@router.message(Command("fetch_news"))
async def cmd_fetch_news(msg: Message, bot: Bot):
    if not is_admin(msg.from_user.id): return
    await msg.answer("⏳ Yangiliklar qidirilmoqda...")
    await post_news_job(bot)
    await msg.answer("✅ Yangiliklar tekshirildi.")


@router.message(Command("fetch_results"))
async def cmd_fetch_results(msg: Message, bot: Bot):
    if not is_admin(msg.from_user.id): return
    await msg.answer("⏳ Natijalar qidirilmoqda...")
    await post_results_job(bot)
    await msg.answer("✅ Natijalar tekshirildi.")

