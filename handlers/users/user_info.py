from aiogram import types, Router
from aiogram.filters import Command

from data.config import db

router = Router()


@router.message(Command("me"))
async def pay(message: types.Message):
    name, balance = await db.get_user_data(message.from_user.id)
    text = f"Ваше имя: {name}\nВаш баланс: {balance}"
    await message.answer(text)
