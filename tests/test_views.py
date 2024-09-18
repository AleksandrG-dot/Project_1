import json
from unittest.mock import Mock

import pandas as pd

import src.utils as utils
import src.views as views

expect_dict = {
    "greeting": "Добрый вечер",
    "cards": [
        {"last_digits": "7197", "total_spent": 2500.0, "cashback": 42.0},
        {"last_digits": "8888", "total_spent": 2024.0, "cashback": 20.0},
    ],
    "top_transactions": [
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
    ],
    "currency_rates": [{"currency": "USD", "rate": 90.00}, {"currency": "GBP", "rate": 118.19}],
    "stock_prices": [{"stock": "MSFT", "price": 401.7}],
}

expected = json.dumps(expect_dict, indent=4, ensure_ascii=False)


# Тестирование функции main (Веб-страница: "Главная")
def test_main(transaction_df):

    # Mock чтения файла настроек user_settings.json в функции get_user_settings в модуле utils
    mock_user_settings = Mock(
        return_value={
            "user_currencies": ["USD", "GBP"],
            "user_stocks": ["MSFT"],
        }
    )
    json.load = mock_user_settings

    # Mock чтения файла Excel operations.xlsx в функции reading_data_excel в модуле utils
    mock_reading_data_excel = Mock(return_value=transaction_df)
    pd.read_excel = mock_reading_data_excel

    # Mock функции приветствия get_greeting в модуле views
    mock_get_greeting = Mock(return_value="Добрый вечер")
    utils.get_greeting = mock_get_greeting

    # Mock функции get_exchange_rate в модуле views
    mock_exchange_rate = Mock(
        return_value=[
            {"currency": "USD", "rate": 90.00},
            {"currency": "GBP", "rate": 118.19},
        ]
    )
    utils.get_exchange_rate = mock_exchange_rate

    # Mock функции get_stock_quotes в модуле views
    mock_stock_rate = Mock(return_value=[{"stock": "MSFT", "price": 401.7}])
    utils.get_stock_quotes = mock_stock_rate

    assert views.main("2020-09-06 20:14:30") == expected
    mock_user_settings.assert_called_once()
    mock_reading_data_excel.assert_called_once()
    mock_get_greeting.assert_called_once()
    mock_exchange_rate.assert_called_once_with(["USD", "GBP"])
    mock_stock_rate.assert_called_once_with(["MSFT"])
