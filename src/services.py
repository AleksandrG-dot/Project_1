""" Сервисы: Поиск переводов физическим лицам """

# Используемые библиотеки json, logging, pytest, regex

# Функция возвращает JSON со всеми транзакциями, которые относятся к переводам физлицам.
# Категория такой транзакции — Переводы, а в описании есть имя и первая буква фамилии с точкой (Валерий А.).

import json
import logging
import re

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(rf"..\\logs\{__name__}.log", "w")
file_formatter = logging.Formatter("%(asctime)s-%(name)s-%(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def get_transfer_to_individual(transactions: list[dict]) -> str:
    """Функция поиск переводов физическим лицам"""
    logger.info("Запуск функции поиска переводов физическим лицам get_transfer_to_individual")
    try:
        result = []
        for trans in transactions:
            if (
                trans.get("Статус").lower() == "failed"
            ):  # С таким значением столбец 'Категория' равен NaN и дальнейший код вызовет исключение
                continue
            if re.search("переводы", trans.get("Категория"), flags=re.I) and re.search(
                r"[\w]+ \w\.", trans.get("Описание"), flags=re.I
            ):
                result.append(trans)
        result_json = json.dumps(result, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Функция get_transfer_to_individual: Произошла ОШИБКА: {e}", exc_info=True)
        raise e
    logger.info("Завершение работы функции get_transfer_to_individual")
    return result_json
