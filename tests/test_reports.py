import datetime

import pytest

import src.reports as reports


# Тестирование функции вычитающей 3 месяца от указанной даты three_month_ago
@pytest.mark.parametrize(
    "date, date_minus_three",
    [
        (datetime.datetime(year=2024, month=2, day=12), datetime.datetime(year=2023, month=11, day=12)),
        (datetime.datetime(year=2024, month=9, day=12), datetime.datetime(year=2024, month=6, day=12)),
    ],
)
def test_three_month_ago(date, date_minus_three):
    assert reports.three_month_ago(date) == date_minus_three


# Тестирование функции отбора трат по категории spending_by_category
def test_spending_by_category(transaction_df):
    res_for_test = reports.spending_by_category(transaction_df, "переводы", "2021.08.15")
    # assert res_for_test['Описание'].to_dict() == {1: 'Игорь С.', 2: 'Ольга И.'}
    assert res_for_test == (
        '[{"Дата операции": "16.05.2021 10:29:04", "Дата платежа": "16.05.2021", "Номер карты":'
        ' NaN, "Статус": "OK", "Сумма операции": -50.0, "Валюта операции": "RUB", "Сумма платежа"'
        ': -50.0, "Валюта платежа": "RUB", "Кэшбэк": NaN, "Категория": "Переводы", "MCC": NaN, '
        '"Описание": "Игорь С.", "Округление на инвесткопилку": 0.0, "Сумма операции с округлени'
        'ем": 50.0}, '
        '{"Дата операции": "16.05.2021 16:02:01", "Дата платежа": "11.05.2021", "Номер карты": '
        'NaN, "Статус": "OK", "Сумма операции": -105.0, "Валюта операции": "RUB", "Сумм'
        'а платежа": -105.0, "Валюта платежа": "RUB", "Кэшбэк": NaN, "Категория": "Переводы", "MC'
        'C": NaN, "Описание": "Ольга И.", "Округление на инвесткопилку": 0.0, "Сумма операции с '
        'округлением": 105.0}]'
    )


# Тестирование функции отбора трат по категории spending_by_category - На эти даты нет транзакций
def test_spending_by_category_no_info(transaction_df):
    res_for_test = reports.spending_by_category(transaction_df, "переводы", "2024.09.12")
    # assert res_for_test['Описание'].to_dict() == {}
    assert res_for_test == "[]"


# Тестирование функции отбора трат по категории spending_by_category - вход и выход - пустой датафрейм
def test_spending_by_category_no_data(transaction_df_zero):
    res_for_test = reports.spending_by_category(transaction_df_zero, "переводы", "2021.08.15")
    # assert res_for_test['Описание'].to_dict() == {}
    assert res_for_test == "[]"


# Тестирование декоратора сохранения результатов в json-файл
def test_save_result():
    tst_data = '[{"Значение 1":1,"Result___2":3},{"Значение 1":2,"Result___2":4},{"Значение 1":"3","Result___2":"5"}]'
    filename = "test.json"

    @reports.save_result(filename=filename)
    def tst_decor():
        return tst_data

    tst_decor()
    with open(filename, "r", encoding="utf-8") as file:
        datafile = file.read()
    assert datafile == tst_data
