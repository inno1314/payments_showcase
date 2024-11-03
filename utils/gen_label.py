import string, random


async def generate_label() -> str:
    """Создает платежный иденификатор из 16 случайных символов ASCII и чисел"""
    return "".join(random.sample(string.ascii_lowercase + string.digits, 16))
