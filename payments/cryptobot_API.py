import logging
from aiocryptopay import AioCryptoPay, Networks
from typing import Tuple

from data.config import CRYPTO_BOT_TOKEN

logger = logging.getLogger(__name__)


class AsyncCryptoPayAPI:
    def __init__(
        self, token: str = CRYPTO_BOT_TOKEN, network: Networks = Networks.TEST_NET
    ):
        """
        Создает API клиента для платежной системы CryptoBot

        :param token: API token для CryptoPay
        :param network: Network type (MAIN_NET or TEST_NET)
        """
        self.crypto = AioCryptoPay(token=token, network=network)

    async def create_payment(
        self, amount: float, currency: str = "RUB"
    ) -> Tuple[str, str]:
        """
        Создает URL для оплаты

        :param amount: Payment amount
        :param currency: Payment currency (default is RUB)
        """
        invoice = await self.crypto.create_invoice(
            amount=float(amount), fiat=currency, currency_type="fiat"
        )
        return invoice.bot_invoice_url, str(invoice.invoice_id)

    async def is_expired(self, invoice_id: str) -> bool:
        """Проверяет статус платежа"""
        invoice_info = await self.crypto.get_invoices(invoice_ids=int(invoice_id))
        return invoice_info.status == "expired"

    async def is_success(self, invoice_id: str) -> bool:
        """Проверяет статус платежа"""
        invoice_info = await self.crypto.get_invoices(invoice_ids=int(invoice_id))
        return invoice_info.status == "paid"

    async def close(self):
        await self.crypto.close()
