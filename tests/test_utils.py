# pytest запускать из папки tests

import datetime
from unittest.mock import patch

import pytest

import src.utils as utils


# Тестирование функции получения приветствия get_greeting
@pytest.mark.parametrize(
    "dt_str, expected",
    [
        ("2024-09-02 22:01:00", "Доброй ночи"),
        ("2024-09-02 04:59:30", "Доброй ночи"),
        ("2024-05-06 05:00:24", "Доброе утро"),
        ("2024-05-06 11:59:59", "Доброе утро"),
        ("2024-05-06 12:00:01", "Добрый день"),
        ("2024-05-06 16:59:01", "Добрый день"),
        ("2024-05-06 17:00:01", "Добрый вечер"),
        ("2024-05-06 21:59:30", "Добрый вечер"),
    ],
)
def test_get_greeting(dt_str, expected):
    assert utils.get_greeting(dt_str) == expected


# Тестирование функции получения приветствия get_greeting - не верные данные
def test_get_greeting_error():
    with pytest.raises(ValueError):
        utils.get_greeting("")

    with pytest.raises(ValueError):
        utils.get_greeting("2024-05-06 24:01:24")


# Тестирование функции get_data_for_month_excel
# Функция читает данные из файла и сразу фильтрует по дате, оставляя только нужные данные
@patch("src.utils.pd.read_excel")
def test_get_data_for_month_excel(moc, transaction_df):
    moc.return_value = transaction_df
    assert utils.get_data_for_month_excel("2020-09-02 20:14:30").loc[:, "Сумма операции"].to_dict() == {
        9: -795.0,
        10: -2024.0,
    }


# Тестирование функции get_data_for_month_excel - дата не содержащая транзакций
@patch("src.utils.pd.read_excel")
def test_get_data_for_month_excel_no_date(moc, transaction_df):
    moc.return_value = transaction_df
    assert utils.get_data_for_month_excel("2024-09-02 20:14:30").loc[:, "Дата операции"].to_dict() == {}


# Тестирование функции получения информации о карте get_card_info
def test_get_card_info(transaction_df):
    assert utils.get_card_info(transaction_df) == [
        {"last_digits": "7197", "total_spent": 2500.0, "cashback": 42.0},
        {"last_digits": "8888", "total_spent": 2024.0, "cashback": 20.0},
    ]


# Тестирование функции получения информации о карте get_card_info - вход - пустой датафрейм
def test_get_card_info_no_data(transaction_df_zero):
    assert utils.get_card_info(transaction_df_zero) == []


# Тестирование функции отбора ТОП-n транзакций get_top_transactions (n=5)
def test_get_top_transactions(transaction_df):
    # Преобрзование даты операции из str в datetime, т.к. в исходном коде DataFrame идет в таком формате
    transaction_df["Дата операции"] = transaction_df["Дата операции"].map(
        lambda dt: datetime.datetime.strptime(str(dt), "%d.%m.%Y %H:%M:%S")
    )
    assert utils.get_top_transactions(transaction_df) == [
        {"date": "04.09.2020", "amount": 3000.0, "category": "Пополнения", "description": "Перевод с карты"},
        {
            "date": "01.09.2020",
            "amount": 2024.0,
            "category": "Покупка AAPL",
            "description": "Покупка через брокера в Telegram",
        },
        {"date": "03.09.2020", "amount": 1032.0, "category": "Фастфуд", "description": "ЗАО Древнерусская шаурма"},
        {
            "date": "02.09.2020",
            "amount": 795.0,
            "category": "Перевод мошенникам на связь",
            "description": "IP-телефония",
        },
        {"date": "03.09.2020", "amount": 510.0, "category": "Транспорт", "description": "ООО Римская конница"},
    ]


# Тестирование функции отбора ТОП-n транзакций get_top_transactions (n=2)
def test_get_top_transactions_2(transaction_df):
    # Преобрзование даты операции из str в datetime, т.к. в исходном коде DataFrame идет в таком формате
    transaction_df["Дата операции"] = transaction_df["Дата операции"].map(
        lambda dt: datetime.datetime.strptime(str(dt), "%d.%m.%Y %H:%M:%S")
    )
    assert utils.get_top_transactions(transaction_df, 2) == [
        {"date": "04.09.2020", "amount": 3000.0, "category": "Пополнения", "description": "Перевод с карты"},
        {
            "date": "01.09.2020",
            "amount": 2024.0,
            "category": "Покупка AAPL",
            "description": "Покупка через брокера в Telegram",
        },
    ]


# Тестирование функции отбора ТОП-n транзакций get_top_transactions - вход - пустой датафрейм
def test_get_top_transactions_no_data(transaction_df_zero):
    assert utils.get_top_transactions(transaction_df_zero) == []


# Тестирование функции получения настроек ползьзователя get_user_settings
# Чтение реального файла. Тесть пройдет если файл не изменен
def test_get_user_settings():
    assert utils.get_user_settings() == {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"],
    }


# Тестирование функции получения значений курса валют get_exchange_rate
@patch("src.utils.requests.get")
def test_get_exchange_rate(moc_get):
    moc_get.return_value.status_code = 200
    moc_get.return_value.json.return_value = {
        "success": True,
        "timestamp": 1725797283,
        "base": "RUB",
        "date": "2024-09-08",
        "rates": {"USD": 0.011111, "GBP": 0.008461},
    }
    assert utils.get_exchange_rate(["USD", "GBP"]) == [
        {"currency": "USD", "rate": 90.00},
        {"currency": "GBP", "rate": 118.19},
    ]


# Тестирование функции получения значений курса валют get_exchange_rate - все валюты неизвестны или ошибочны
# Возврат - пустой список
@patch("src.utils.requests.get")
def test_get_exchange_rate_non_curr(moc_get):
    moc_get.return_value.status_code = 400
    moc_get.return_value.json.return_value = {
        "error": {
            "code": "invalid_currency_codes",
            "message": "You have provided one or more invalid Currency Codes. "
            "[Required format: currencies=EUR,USD,GBP,...]",
        }
    }
    assert utils.get_exchange_rate(["ARB", "TSLA"]) == []
    moc_get.assert_called_once()


# Тестирование функции получения значений курса валют get_exchange_rate - 3 значения валют: 2 - не верных, 1 - верна
# Возврат - список из одного словаря с курсом верной валюты
@patch("src.utils.requests.get")
def test_get_exchange_rate_one_valid(moc_get):
    moc_get.return_value.status_code = 200
    moc_get.return_value.json.return_value = {
        "success": True,
        "timestamp": 1725811563,
        "base": "RUB",
        "date": "2024-09-08",
        "rates": {"USD": 0.011111},
    }
    assert utils.get_exchange_rate(["ARB", "TSLA", "USD"]) == [{"currency": "USD", "rate": 90.0}]
    moc_get.assert_called_once()


# Тестирование функции получения текущих котировок по финансовым инструментам get_stock_quotes
# Количество входных тикеров: 1
@patch("src.utils.requests.get")
def test_get_stock_quotes(moc_get):
    moc_get.return_value.status_code = 200
    moc_get.return_value.json.return_value = {
        "Global Quote": {
            "01. symbol": "MSFT",
            "02. open": "409.0600",
            "03. high": "410.6500",
            "04. low": "400.8000",
            "05. price": "401.7000",
            "06. volume": "19609526",
            "07. latest trading day": "2024-09-06",
            "08. previous close": "408.3900",
            "09. change": "-6.6900",
            "10. change percent": "-1.6381%",
        }
    }
    assert utils.get_stock_quotes(["MSFT"]) == [{"stock": "MSFT", "price": 401.7}]
    moc_get.assert_called_once()


# Тестирование функции получения текущих котировок по финансовым инструментам get_stock_quotes
# Количество входных тикеров: 2.
@patch("src.utils.requests.get")
def test_get_stock_quotes_2(moc_get):
    moc_get.return_value.status_code = 200
    moc_get.return_value.json.return_value = {
        "Global Quote": {
            "01. symbol": "AAPL",
            "02. open": "223.9500",
            "03. high": "225.2400",
            "04. low": "219.7700",
            "05. price": "220.8200",
            "06. volume": "48423011",
            "07. latest trading day": "2024-09-06",
            "08. previous close": "222.3800",
            "09. change": "-1.5600",
            "10. change percent": "-0.7015%",
        }
    }
    assert utils.get_stock_quotes(["AAPL", "AAPL"]) == [
        {"stock": "AAPL", "price": 220.82},
        {"stock": "AAPL", "price": 220.82},
    ]
    moc_get.assert_called()


# Тестирование функции получения текущих котировок по финансовым инструментам get_stock_quotes
# Количество входных тикеров: 2 - не верных. Цена вернется равная 0.
@patch("src.utils.requests.get")
def test_get_stock_quotes_no_data(moc_get):
    moc_get.return_value.status_code = 200
    moc_get.return_value.json.return_value = {"Global Quote": {}}
    assert utils.get_stock_quotes(["AAAA", "BB"]) == [{"stock": "AAAA", "price": 0.0}, {"stock": "BB", "price": 0.0}]
    moc_get.assert_called()


# Тестирование функции получения текущих котировок по финансовым инструментам get_stock_quotes
# Закончился лимит запросов. Количество входных тикеров: 2.
# Вернет либо пустой список, либо список с уже обработнными запросами до возникновения ошибки
@patch("src.utils.requests.get")
def test_get_stock_quotes_limit(moc_get):
    moc_get.return_value.status_code = 200
    moc_get.return_value.json.return_value = {
        "Information": "Thank you for using Alpha Vantage! Our standard API rate limit is 25 requests per day. "
        "Please subscribe to any of the premium plans at https://www.alphavantage.co/premium/ "
        "to instantly remove all daily rate limits."
    }
    assert utils.get_stock_quotes(["SKPR", "KO"]) == []
    moc_get.assert_called_once()  # так как ошибка возникла на первом тикере, функция не пойдет проверять второй тикер
