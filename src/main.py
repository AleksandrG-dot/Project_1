""" Модуль с реализованными в проекте функциональностями """

import json

import src.reports as reports
import src.services as services
import src.utils as utils
import src.views as views

if __name__ == "__main__":
    print("_____ Веб-страница: Главная _____")
    print(views.main("2020-09-07 20:14:30"))

    print()
    print("_____ Отчеты: Траты по категории _____")
    print("Категория: Переводы. Диапазон дат: 2020.06.07 - 2020.09.07")
    transactions = utils.reading_data_excel()  # чтения данных с транзакциями
    transfers_json = reports.spending_by_category(transactions, "Переводы", "2020.09.07")
    # Преобразование в python-объект для удобства вывода в консоль и дальнейшей обработки
    transfers_dict = json.loads(transfers_json)
    for transfer in transfers_dict:
        print(transfer)

    print()
    print("_____ Сервисы: Поиск переводов физическим лицам _____")
    # Как входные данные использует результаты предыдущей функции отбора по категории spending_by_category
    transfers_to_individuals_json = services.get_transfer_to_individual(transfers_dict)
    # Преобразование в python-объект для удобства вывода в консоль
    transfers_to_individuals_dict = json.loads(transfers_to_individuals_json)
    for transfer in transfers_to_individuals_dict:
        print(transfer)
