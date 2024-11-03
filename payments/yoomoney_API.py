import logging
from yoomoney import Client, Quickpay
from typing import Tuple
from data.config import YOOMONEY_TOKEN, YOOMONEY_WALLET
from utils.gen_label import generate_label

logger = logging.getLogger(__name__)


class AsyncYoomoneyAPI:
    def __init__(self, receiver: str = YOOMONEY_WALLET, token: str = YOOMONEY_TOKEN):
        """
        Создает API клиента для платежной системы ЮМани

        :param receiver: номер кошелька получателя
        :param YOOMONEY_TOKEN: Ваш ACCESS_TOKEN
        """
        self.receiver = receiver
        self.token = token

    async def create_payment(
        self,
        amount: float,
        targets: str = "Цифровая услуга",
        paymentType: str = "SB",
    ) -> Tuple[str, str]:
        """
        Создает URL для оплаты

        :param payment_id: Номер заказа в вашей системе
        :param amount: Сумма платежа
        :param targets: Название вашего приложения
        :param paymentType: Тип оплаты

        Returns: Payment URL
        """
        payment_id = await generate_label()
        quick_pay = Quickpay(
            receiver=self.receiver,
            quickpay_form="shop",
            targets=targets,
            paymentType=paymentType,
            sum=amount,
            label=payment_id,
        )
        return quick_pay.redirected_url, payment_id

    async def get_payment_info(self, payment_id: str):
        """
        Создает запрос для получения информации о платеже

        :param order_id: Номер заказа в вашей системе

        :return: Model from response JSON
        """
        client = Client(self.token)
        try:
            history = client.operation_history(label=payment_id)
            if history.operations:
                return history.operations[-1]
            else:
                return None
        except Exception as e:
            logger.info(f"Error fetching payment info: {e}")
            return None

    async def is_expired(self, payment_id: str) -> bool:
        """Проверяет статус платежа"""
        operation = await self.get_payment_info(payment_id)
        if operation is not None:
            return operation.status == "refused"
        return False

    async def is_success(self, payment_id: str) -> bool:
        """Проверяет статус платежа"""
        operation = await self.get_payment_info(payment_id)
        return operation is not None and operation.status == "success"

    async def close(self) -> None:
        pass
