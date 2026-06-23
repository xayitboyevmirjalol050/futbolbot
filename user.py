from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
import database as db

router = Router()


@router.message(CommandStart())
async def cmd_start(msg: Message):
    u = msg.from_user
    await db.add_user(u.id, u.username or "", u.full_name or "")
    await msg.answer(
        f"⚽ Salom, <b>{u.full_name}</b>!\n\n"
        "Futbol yangiliklari va natijalarini kuzatish uchun kanalimizga obuna bo'ling. "
        "Bot avtomatik ravishda eng so'nggi yangiliklar va o'yin natijalarini o'zbek tilida yetkazib beradi.",
        parse_mode="HTML"
    )


@router.message()
async def handle_any(msg: Message):
    u = msg.from_user
    await db.add_user(u.id, u.username or "", u.full_name or "")
