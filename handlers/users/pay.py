import logging
from aiogram import types, Router, F
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext

from data.config import db
from states.pay import Payments
from payments import process_payment

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("pay"))
async def pay(message: types.Message, command: CommandObject, state: FSMContext):
    arg = command.args
    if arg is None:
        await message.answer("Неправильно указана сумма!")
        return
    try:
        amount = int(arg)
    except:
        await message.answer("Неправильно указана сумма!")
        return
    if amount < 50 or amount > 10000:
        await message.answer("Неправильная сумма!")
        return

    await state.set_state(Payments.choose_service)
    await state.update_data(amount=amount)
    text = (
        "Выберите способ оплаты: \n\n"
        "/yoomoney — Карта РФ\n"
        "/cryptobot — Крипта\n"
        "/aaio — Карта UA / Крипта / СБП\n"
    )
    await message.answer(text)


@router.message(
    Payments.choose_service, F.text.in_(["/yoomoney", "/cryptobot", "/aaio"])
)
async def payment(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    amount = state_data["amount"]
    payment_type = message.text[1:]
    logger.info(
        f"Сгенерирована платежная ссылка {payment_type} на сумму {amount} рублей"
    )
    await process_payment(message=message, price=amount, system=payment_type)
    await state.clear()

@router.callback_query(F.data == "cancel_payment")
async def cancel_payment(call: types.CallbackQuery):
    await db.update_label(label="1", user_id=call.from_user.id)
    await call.message.edit_text("Платеж отменен")
