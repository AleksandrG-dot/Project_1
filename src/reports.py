""" Отчеты: Траты по категориям """

import datetime
import json
import logging
from functools import wraps
from typing import Optional

import pandas as pd

# Используемые библиотеки json, pandas, logging, pytest, datetime
# Функция принимает на вход: датафрейм с транзакциями, название категории, опциональную дату.
# Если дата не передана, то берется текущая дата.
# Функция возвращает траты по заданной категории за последние три месяца (от переданной даты).

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(rf"..\\logs\{__name__}.log", "w")
file_formatter = logging.Formatter("%(asctime)s-%(name)s-%(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def save_result(filename=""):
    """Декоратор для сохранения работы функции в файл json. Декорируемая функция должна возвращать строку JSON"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            if filename:
                fname = filename
            else:
                fname = f"{func.__name__}.json"
            logger.info(f"Сохранение декоратором save_result файла {fname}")
            with open(fname, "w", encoding="utf-8") as f:
                f.write(res)
            return res

        return wrapper

    return decorator


def three_month_ago(dt: datetime) -> datetime:  # Не нашел другого способа вычесть 3 месяца (timedelta с месяцами
    """Функция вычитающая 3 месяца"""  # не работает, calendar не знает месяцы -1, -2, -3
    logger.info("Запуск функции вычитания 3 месяцев three_month_ago")
    if dt.month < 4:
        result = datetime.datetime(dt.year - 1, 9 + dt.month, dt.day)
    else:
        result = datetime.datetime(dt.year, dt.month - 3, dt.day)
    logger.info("Завершение работы функции three_month_ago")
    return result


@save_result()
def spending_by_category(
    transactions: pd.DataFrame, category: str, date: Optional[str] = None
) -> str:  # Дата: YYYY.MM.DD
    """Функция отбора трат по указанной категории. Формат даты: YYYY.MM.DD"""
    logger.info("Запуск функции отбора трат по категории spending_by_category")
    try:  # Если где-то в коде возникнет ошибка, это позволит ее залоггировать
        if transactions.empty:
            logger.info("В функцию spending_by_category передан пустой DataFrame")
            return "[]"  # json.dumps(transactions.to_dict(orient='records'), ensure_ascii=False)
        if not date:  # Если дата не указана, берем текущую
            input_date = datetime.datetime.now()
        else:
            input_date = datetime.datetime.strptime(date, "%Y.%m.%d")
        end_date = datetime.datetime(input_date.year, input_date.month, input_date.day, 23, 59, 59)
        start_date = three_month_ago(end_date)

        # Если в DataFrame время не datetime, то преобразуем в datetime
        if not isinstance(transactions.loc[0, "Дата операции"], pd._libs.tslibs.timestamps.Timestamp):
            transactions["Дата операции"] = transactions["Дата операции"].map(
                lambda dt: datetime.datetime.strptime(str(dt), "%d.%m.%Y %H:%M:%S")
            )

        # Фильтрация транзакций за 3 месяца
        filter_trans = transactions[
            (start_date <= transactions["Дата операции"])
            & (transactions["Дата операции"] <= end_date)
            & (transactions["Категория"] == category.title())
        ]

        filter_trans_dict = filter_trans.to_dict(orient="records")  # Преобразование в словарь

        # Преобразование времение в "Дате операции" из datetime в str. Иначе не преобразуется в JSON.
        # Преобразовать в DataFrame не получилось.
        for i in range(len(filter_trans_dict)):
            filter_trans_dict[i]["Дата операции"] = filter_trans_dict[i]["Дата операции"].strftime("%d.%m.%Y %H:%M:%S")

        filter_trans_json = json.dumps(filter_trans_dict, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Функция spending_by_category: Произошла ОШИБКА: {e}", exc_info=True)
        raise e
    logger.info("Завершение работы функции spending_by_category")
    return filter_trans_json
