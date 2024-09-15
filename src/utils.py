import datetime
import json
import logging
import os

import pandas as pd
import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(rf"..\\logs\{__name__}.log", "w")
file_formatter = logging.Formatter("%(asctime)s-%(name)s-%(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def get_user_settings() -> dict():
    """Функции получения настроек ползьзователя из файла user_settings.json"""
    path = "user_settings.json"
    logger.info(f"Запуск функции получения настроек get_user_settings из {path}")
    if not os.path.exists(path):  # Если запуск произойдет не из корня проекта
        path = r"..\user_settings.json"
        if not os.path.exists(path):
            logger.error("Файл user_settings.json с настройками пользователя не найден.")
            return {"Error": "Файл user_settings.json не найден."}
    try:  # Проверка что формат файла соответствует требованиям и в нем есть нужные нам ключи
        with open(path) as file:
            result = json.load(file)
        result["user_currencies"]
        result["user_stocks"]
    except Exception as e:
        logger.error(f"Функция get_user_settings: Произошла ОШИБКА: {e}", exc_info=True)
    logger.info("Завершение работы функции get_user_settings")
    return result


def get_greeting(dt_str: str = "now") -> str:  # дата YYYY-MM-DD HH:MM:SS
    """Функция возвращает строку приветствия в зависимости от времени суток"""
    # Реализовал функцию с возможностью передавать время в формете YYYY-MM-DD HH:MM:SS, так как считаю что время должен
    # передавать клиент, а не сервер брать свое, так как они могут находиться в разных часовых поясах.
    # По умолчанию, если в функцию не передавать дату-время, то возьмется текущее с сервера.
    logger.info("Запуск функции получения строки приветствия get_greeting")
    try:
        if dt_str != "now":
            dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        else:
            dt = datetime.datetime.now()
    except Exception as e:
        logger.error(f"Функция get_greeting: Произошла ОШИБКА: {e}", exc_info=True)
        raise e
    if 5 <= dt.hour <= 11:
        result = "Доброе утро"
    elif 12 <= dt.hour <= 16:
        result = "Добрый день"
    elif 17 <= dt.hour <= 21:
        result = "Добрый вечер"
    else:
        result = "Доброй ночи"
    logger.info("Завершение работы функции get_greeting")
    return result


def reading_data_excel() -> pd.DataFrame:
    """Функция чтения данных о транзакциях из Exel-файла data/operations.xlsx"""
    logger.info(r"Запуск функции чтения данных транзакций reading_data_excel из data\operations.xlsx")
    path = r"data\operations.xlsx"
    if not os.path.exists(path):  # Если запуск произойдет не из корня проекта
        path = r"..\\data\operations.xlsx"
        if not os.path.exists(path):
            logger.error(r"Файл \data\operations.xlsx с данными не найден.")
            raise FileNotFoundError(r"Файл \data\operations.xlsx не найден.")
    try:
        result = pd.read_excel(path)
    except Exception as e:
        logger.critical(f"Функция reading_data_excel. Ошибка чтения: {e}", exc_info=True)
        raise e
    logger.info("Завершение работы функции reading_data_excel")
    return result


def get_data_for_month_excel(dt_str: str) -> pd.DataFrame:  # дата YYYY-MM-DD HH:MM:SS
    """Функция принимает дату, читает файл с транзакциями operations.xlsx, фильтрует транзакции с начала месяца,
    на который выпадает входящая дата, по входящую дату"""
    logger.info("Запуск функции фильтрации транзакций get_data_for_month_excel")
    try:
        # Создание дат для фильтрования транзакций. Тип - datetime
        input_date = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.datetime(input_date.year, input_date.month, input_date.day, 23, 59, 59)
        start_date = datetime.datetime(end_date.year, end_date.month, 1)
    except Exception as e:  # Если есть какая-либо ошибка с форматом даты
        logger.error(f"Функция get_data_for_month_excel. Ошибка даты: {e}", exc_info=True)
        raise e

    # Чтение транзакций отдельной функцией
    data_excel = reading_data_excel()

    # Преобразование колонки Дата операции из str в datetime
    data_excel["Дата операции"] = data_excel["Дата операции"].map(
        lambda dt: datetime.datetime.strptime(str(dt), "%d.%m.%Y %H:%M:%S")
    )

    # Фильтрация транзакций от начала месяца до указанной даты
    result = data_excel[(start_date <= data_excel["Дата операции"]) & (data_excel["Дата операции"] <= end_date)]

    logger.info("Завершение работы функции get_data_for_month_excel")
    return result


def get_card_info(df: pd.DataFrame) -> list[dict]:
    """Функция возвращает список словарей с данными по каждой карте.
    Данные: последние 4 цифры карты, общая сумма расходов, сумму кешбека"""
    logger.info("Запуск функции анализа карт get_card_info")

    # Удаляет операции с пополнением карт, оставляет только расходные операции
    df = df.loc[df["Сумма операции"] < 0]

    # Удаляет неуспешные операции
    df = df.loc[df["Статус"] == "OK"]

    # Считает кешбек и заполняет пустое поле, если отсутствует (1 рубль на каждые 100 рублей)
    for i, row in df.iterrows():
        if not (row["Кэшбэк"] > 0 or row["Кэшбэк"] < 0):
            df.loc[i, "Кэшбэк"] = abs(df.loc[i, "Сумма операции"]) // 100

    # Группировка по номеру карты и подсчет
    card_info = df.groupby("Номер карты").agg({"Сумма операции": "sum", "Кэшбэк": "sum"})

    # Преобразование готового DataFrame в требуемый формат ответа - list[dict]
    result = []
    for card, info in card_info.to_dict(orient="index").items():
        result.append(
            {
                "last_digits": card.replace("*", ""),
                "total_spent": info["Сумма операции"] * -1,
                "cashback": info["Кэшбэк"],
            }
        )
    logger.info("Завершение работы функции get_card_info")
    return result


def get_top_transactions(df: pd.DataFrame, n: int = 5) -> list[dict]:
    """Функция возвращает список словарей с данными Топ-n транзакций. По умолчанию n=5.
    Данные: дата, сумма транзакции, категория, описание"""
    logger.info(f"Запуск функции Топ-{n} транзакций get_top_transactions")

    # Удаляет неуспешные операции
    df = df.loc[df["Статус"] == "OK"]

    # Если не далать df_2, а поставить inplace=True (а так я считаю правильнее), то pytest будет
    # заколебывать с warningom. Хотя на старой фикстуре работало Ok (без добавленгия новых 4 транзакций спереди)
    df_2 = df.sort_values(by="Сумма операции с округлением", ascending=False, inplace=False)

    # Преобразование первых n транзакций в требуемый формат
    result = []
    for _, row in df_2.head(n).iterrows():
        result.append(
            {
                "date": datetime.datetime.strftime(row["Дата операции"], "%d.%m.%Y"),
                "amount": abs(row["Сумма операции"]),
                "category": row["Категория"],
                "description": row["Описание"],
            }
        )

    logger.info("Завершение работы функции get_top_transactions")
    return result


def get_exchange_rate(currencies: list[str]) -> list[dict]:
    """Функция получения курса валют через API"""
    logger.info(f'Запуск функции получения курса валют через API - get_exchange_rate. Валюты: {", ".join(currencies)}')
    url = "https://api.apilayer.com/exchangerates_data/latest"

    try:  # Все операции в try except, так как много мест где может произойти отказ (нет интернет, нет .env)
        # Чтение api-ключа
        load_dotenv()
        headers = {"apikey": str(os.getenv("APILAYER_KEY"))}

        # За базовую валюту выбрал RUB, что бы делать один запрос вместо двух. Значения "переверну" дальше.
        payload = {"symbols": ",".join(currencies), "base": "RUB"}
        response = requests.get(url, headers=headers, params=payload)

        result = []
        if response.status_code == 200:
            for crnc, rate in response.json()["rates"].items():
                result.append({"currency": crnc, "rate": round(1 / rate, 2)})
            logger.info("Данные по курсу валют успешно получены")
        else:
            logger.error(f"Ошибка запроса курса валют. Status code: {response.status_code}")
    except Exception as e:
        logger.error(f"Функция get_exchange_rate: Произошла ОШИБКА: {e}")
        raise e
    logger.info("Завершение работы функции get_exchange_rate.")
    return result


def get_stock_quotes(tickers: list[str]) -> list[dict]:
    """Функция получения текущих котировок по финансовым инструментам (акции, валютные пары)
    На вход принимает сисок инструментов, возвращает список словарей.
    Если рынки закрыты, вернется цена закрытия."""
    logger.info(f'Запуск функции получения котировок через API - get_stock_quotes. Тикеры: {", ".join(tickers)}')
    url = "https://www.alphavantage.co/query"  # Бесплатно 25 запросов в день

    try:  # Все операции в try except, так как много мест где может произойти отказ (нет интернет, нет .env)
        # Чтение api-ключа
        load_dotenv()
        alphaventage_key = os.getenv("ALPHAVENTAGE_KEY")

        result = []
        for ticker in tickers:
            payload = {"function": "GLOBAL_QUOTE", "symbol": ticker, "apikey": alphaventage_key}
            response = requests.get(url, params=payload)
            if response.status_code == 200:
                res_json = response.json()
                if "Global Quote" not in res_json:  # Если нет этого ключа, значит какая-то ошибка
                    # Скорее всего закончился лимит запросов
                    logger.error(
                        f"Запрос не удался. Завершение работы функции get_stock_quotes. Тикер: {ticker}. "
                        f"\n Ответ сервера: {res_json}"
                    )
                    return result  # Вернет либо пустой список, либо список с уже обработнными запросами
                price = res_json.get("Global Quote").get("05. price")

                if not price:  # Если пустой прайс, значит тикер не был найден
                    price = 0
                    logger.warning(f"Запрос не удался. Не верный тикер: {ticker}")
                result.append({"stock": ticker, "price": round(float(price), 2)})
            else:
                logger.error(f"Ошибка запроса котировок. Status code: {response.status_code}")
    except Exception as e:
        logger.error(f"Функция get_stock_quotes: Произошла ОШИБКА: {e}")
        raise e
    logger.info("Завершение работы функции get_stock_quotes.")
    return result
