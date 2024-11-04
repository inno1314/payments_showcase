import logging, time, asyncio

from aiogram import types
from typing import Literal

from data.config import db
from utils.create_link import link_keyboard
from payments import (
    AsyncYoomoneyAPI,
    AsyncAaioAPI,
    AsyncCryptoPayAPI,
)

logger = logging.getLogger(__name__)

clients = {
    "yoomoney": AsyncYoomoneyAPI(),
    "aaio": AsyncAaioAPI(),
    "cryptobot": AsyncCryptoPayAPI(),
}


async def process_payment(
    message: types.Message,
    price: int,
    system: Literal["yoomoney", "aaio", "cryptobot"],
):
    """
    Проверяет оплату во всех платежных системах
    :param message: aiogram.types.Message
    :param price: Сумма создаваемого платежа
    :param system: Система, в которой совершается платеж.
    """
    user_id = message.from_user.id
    client = clients[system]

    url, payment_id = await client.create_payment(amount=price)
    await db.create_payment(
        user_id=user_id,
        amount=price,
        service=system,
        payment_id=payment_id,
    )
    await db.update_label(user_id=user_id, label=payment_id)

    markup = await link_keyboard(url)
    new_msg = await message.answer(
        text="Перейдите по ссылке, чтобы пополнить баланс ✅",
        reply_markup=markup,
    )

    start_time = time.time()
    while time.time() - start_time < 600:  # Проверяем в течение 10 минут
        await asyncio.sleep(30)  # Ждем 30 секунд перед следующей проверкой
        logger.info(f"Проверка статуса оплаты пользователя {user_id} в {system}")
        try:
            label = await db.get_label(user_id=user_id)

            if label != payment_id:
                await client.close()
                logger.info(f"Платеж в {system} завершен: label != start_label")
                await db.change_payment_status(
                    payment_id=payment_id,
                    status="expired",
                )
                return

            if await client.is_success(payment_id):
                # Обработка успешного платежа
                await client.close()
                await db.change_payment_status(
                    payment_id=payment_id,
                    status="successful",
                )
                user_data = await db.get_user_data(user_id=user_id)
                current_balance = user_data[1]
                new_balance = current_balance + price
                await db.update_balance(user_id=user_id, amount=new_balance)
                await new_msg.edit_text(f"Успех! Ваш баланс: {new_balance}")
                return
            elif await client.is_expired(payment_id):
                # Обработка истекшего платежа
                await db.change_payment_status(
                    payment_id=payment_id,
                    status="expired",
                )
                await db.update_label(user_id=user_id, label="1")
                await new_msg.edit_text(
                    text="Нам не удалось обработать ваше платеж"
                )
                await client.close()
                logger.info(f"Платеж в {system} для пользователя {user_id} истек")
                return
        except Exception as e:
            logger.info(f"Ошибка в процессе обработки платежа в {system}: {e}")

    # Время ожидания истекло
    logger.info(f"Время оплаты в {system} для пользователя {user_id} истекло")
    await client.close()
    await db.change_payment_status(
        payment_id=payment_id,
        status="expired",
    )
    await new_msg.edit_text(text="Нам не удалось обработать ваше платеж")
