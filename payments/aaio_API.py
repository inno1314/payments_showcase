import hashlib
import logging
from requests import post
from requests.exceptions import RequestException
from typing import Tuple
from data.config import AAIO_API_KEY, AAIO_SECRET_KEY, AAIO_MERCHANT_ID
from utils.gen_label import generate_label

import aiohttp

logger = logging.getLogger(__name__)


class AsyncAaioAPI:
    def __init__(
        self,
        API_KEY: str = AAIO_API_KEY,
        SECRET_KEY: str = AAIO_SECRET_KEY,
        MERCHANT_ID: str = AAIO_MERCHANT_ID,
    ):
        """
        Создает API клиента для одного мерчанта в AAIO

        :param MERCHANT_ID: Merchant ID из https://aaio.so/cabinet
        :param SECRET_KEY: 1-ый secret key из https://aaio.so/cabinet
        :param API_KEY: API key из https://aaio.so/cabinet/api
        """

        self.API_KEY = API_KEY
        self.SECRET_KEY = SECRET_KEY
        self.MERCHANT_ID = MERCHANT_ID

    async def create_payment(
        self,
        amount: float,
        lang: str | None = "ru",
        currency: str | None = "RUB",
        description: str | None = None,
    ) -> Tuple[str, str]:
        """
        Создает URL для оплаты
        См. https://wiki.aaio.so/priem-platezhei/sozdanie-zakaza-zaprosom-rekomenduem для более детальной информации

        :param amount: Сумма платежа
        :param order_id: Номер заказа в вашей системе
        :param description: Описание платежа (не обязательно)
        :param currency: Валюта оплаты (по умолчанию рубли)
        :param language: Язык страницы с оплатой (по умолчанию русский)
        """
        payment_id = await generate_label()
        merchant_id = self.MERCHANT_ID  # merchant id
        secret = self.SECRET_KEY  # secret key №1 из настроек магазина

        sign = f":".join(
            [str(merchant_id), str(amount), str(currency), str(secret), str(payment_id)]
        )

        payload = {
            "merchant_id": merchant_id,
            "amount": amount,
            "currency": currency,
            "order_id": payment_id,
            "sign": hashlib.sha256(sign.encode("utf-8")).hexdigest(),
            "desc": description,
            "lang": lang,
        }

        headers = {"Accept": "application/json"}

        try:
            response = post(
                "https://aaio.so/merchant/get_pay_url",
                headers=headers,
                data=payload,
                timeout=(15, 60),
            )
            response.raise_for_status()  # Проверка статуса ответа
        except RequestException as e:
            logger.info(f"Connect error: {e}")
            raise RequestException

        # Проверка кода ответа
        if response.status_code not in [200, 400, 401]:
            logger.info(f"Response code: {response.status_code}")
            raise RequestException

        try:
            decoded = response.json()  # Парсинг результата
        except ValueError:
            logger.info("Не удалось пропарсить ответ")
            raise ValueError

        if decoded.get("type") == "success":
            return decoded["url"], payment_id
        else:
            logger.info(f'Ошибка: {decoded.get("message", "Unknown error")}')
            raise ValueError

    async def get_payment_info(self, order_id):
        """
        Создает запрос для получения информации о платеже
        См. https://wiki.aaio.so/api/informaciya-o-zakaze

        :param order_id: Номер заказа в вашей системе

        :return: Model from response JSON
        """

        URL = "https://aaio.so/api/info-pay"

        params = {"merchant_id": self.MERCHANT_ID, "order_id": order_id}

        headers = {"Accept": "application/json", "X-Api-Key": self.API_KEY}

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(URL, data=params) as response:
                response_json = await response.json()

                return response_json

    async def is_expired(self, order_id):
        """Проверяет статус платежа"""

        response_json = await self.get_payment_info(order_id)

        return (
            response_json["type"] == "success" and response_json["status"] == "expired"
        )

    async def is_success(self, order_id):
        """Проверяет статус платежа"""

        response_json = await self.get_payment_info(order_id)
        # print(response_json)

        return (
            response_json["type"] == "success" and response_json["status"] == "success"
        ) or (response_json["type"] == "success" and response_json["status"] == "hold")

    async def close(self) -> None:
        pass
