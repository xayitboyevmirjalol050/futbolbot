from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_main_menu() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="👥 Obunachilar", callback_data="admin_users"),
        InlineKeyboardButton(text="📊 Statistika",  callback_data="admin_stats"),
    )
    b.row(
        InlineKeyboardButton(text="📢 E'lon yuborish", callback_data="admin_broadcast"),
        InlineKeyboardButton(text="📋 E'lonlar",       callback_data="admin_broadcasts"),
    )
    b.row(
        InlineKeyboardButton(text="⚡ Yangilik qo'lda joylash",  callback_data="admin_manual_news"),
        InlineKeyboardButton(text="⚽ Natija qo'lda joylash",    callback_data="admin_manual_result"),
    )
    b.row(InlineKeyboardButton(text="❌ Yopish", callback_data="close"))
    return b.as_markup()


def back_btn() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_back"))
    return b.as_markup()


def confirm_broadcast_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="✅ Yuborish",       callback_data="broadcast_yes"),
        InlineKeyboardButton(text="❌ Bekor qilish",   callback_data="broadcast_no"),
    )
    return b.as_markup()


def users_nav(page: int, total_pages: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"users_page_{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="noop"))
    if page < total_pages:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"users_page_{page+1}"))
    b.row(*nav)
    b.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_back"))
    return b.as_markup()
