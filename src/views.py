""" Веб-страница: "Главная" """

# Используемые библиотеки json, requests, API, datetime, logging, pytest, pandas
import json

import utils


def main(dt_as_str: str):  # -> json ????
    """Главная функция выводящая JSON-результ запроса по дате"""

    user_setting = utils.get_user_settings()
    data = utils.get_data_for_month_excel(dt_as_str)
    result = {
        "greeting": utils.get_greeting(),  # Можно передать dt_as_str
        "cards": utils.get_card_info(data),
        "top_transactions": utils.get_top_transactions(data),
        "currency_rates": utils.get_exchange_rate(user_setting.get("user_currencies", [])),
        "stock_prices": utils.get_stock_quotes(user_setting.get("user_stocks", [])),
    }
    return json.dumps(result, indent=4, ensure_ascii=False)
