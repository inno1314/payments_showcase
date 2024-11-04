import sqlite3, logging
from datetime import date
from typing import Tuple, Literal

logger = logging.getLogger(__name__)


class UsersDataBase:
    """Класс для работы с базой данных."""
    def __init__(self, db_file):
        self.connect = sqlite3.connect(db_file)
        self.cursor = self.connect.cursor()

    async def add_user(self, user_id: int, name: str | None = None) -> None:
        """
        Добавляет нового пользователя в БД.
        :param user_id: Telegram ID пользователя.
        :param name: Имя пользователя.
        """
        with self.connect:
            self.cursor.execute(
                """INSERT INTO users (user_id, name) VALUES (?, ?)""",
                [user_id, name],
            )
        logger.info(f"Пользователь {user_id} добавлен в БД.")

    async def user_exists(self, user_id: int) -> bool:
        """Проверяет, существует ли пользователь с таким ID в БД."""
        with self.connect:
            result = self.cursor.execute(
                """SELECT * FROM users WHERE user_id=(?)""", [user_id]
            ).fetchall()
            return bool(len(result))

    async def update_label(self, label: str, user_id: int) -> None:
        """Обновляет платежный идентификатор пользователя."""
        with self.connect:
            self.cursor.execute(
                """UPDATE users SET label=(?) WHERE user_id=(?)""", [label, user_id]
            )
        logger.info(f"Установлен label {label} для пользователя {user_id}")

    async def get_label(self, user_id: int) -> str:
        """Возвращает платежный идентификатор пользователя."""
        with self.connect:
            data = self.cursor.execute(
                """SELECT label FROM users WHERE user_id=(?)""", [user_id]
            ).fetchall()
            return data[0][0]

    async def get_user_data(self, user_id: int) -> Tuple[str, int]:
        """Возвращает имя и баланс пользователя с заданным ID."""
        with self.connect:
            data = self.cursor.execute(
                """SELECT name, balance FROM users WHERE user_id=(?)""",
                [user_id],
            ).fetchall()
            return data[0]

    async def update_balance(self, user_id: int, amount: int) -> None:
        """Обновляет значение баланса для пользователя."""
        with self.connect:
            self.cursor.execute(
                """UPDATE users SET balance=(?) WHERE user_id=(?)""",
                [amount, user_id],
            )
        logger.info(f"Баланс пользователя {user_id} теперь {amount}")

    async def create_payment(
        self,
        payment_id: str,
        user_id: int,
        amount: int,
        service: Literal["aaio", "cryptobot", "yoomoney"],
    ):
        """Создает запись о платеже в БД."""
        today = date.today().strftime("%d.%m.%Y")
        with self.connect:
            self.cursor.execute(
                """INSERT INTO payments 
                (payment_id, user_id, amount, service, date) VALUES (?, ?, ?, ?, ?)""",
                [payment_id, user_id, amount, service, today],
            )
        logger.info(f"Платеж {payment_id} был добавлен в БД.")

    async def change_payment_status(
        self, payment_id: str, status: Literal["successful", "expired"]
    ):
        """Меняет статус о платеже в БД."""
        with self.connect:
            self.cursor.execute(
                """UPDATE payments SET status=(?) WHERE payment_id=(?)""",
                [status, payment_id],
            )
        logger.info(f"Статус платежа {payment_id} установлен на {status}")
