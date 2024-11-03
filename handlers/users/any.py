from aiogram import types, Router
from data.config import db

router = Router()


@router.message()
async def start(message: types.Message):
    user = message.from_user
    if not user:
        return
    if not await db.user_exists(user_id=user.id):
        await db.add_user(user_id=user.id, name=user.username)
    text = "Привет!" if user.username is None else f"Привет!, {user.username}\n\n"
    text += "Пропиши команду /pay `сумма`, чтобы пополнить свой баланс!"
    await message.answer(text)
