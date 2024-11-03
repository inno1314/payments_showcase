from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def link_keyboard(payment_link):
    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Перейти к оплате 🔥',
                                     url=payment_link)
            ],
            [
                InlineKeyboardButton(text='Отмена покупки 🔙',
                                     callback_data='cancel_payment')
            ]
        ]
    )
    return buttons

