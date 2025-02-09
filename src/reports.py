import calendar
import datetime
import json
import logging
import os
from typing import Any

import pandas as pd

logger = logging.getLogger("reports")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("logs/reports.log", encoding="UTF-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def log_to_file(path: str = "data/reports.txt"):
    """Декоратор логирования в файл"""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    logger.info("Начало работы функции логирования в файл")

    def write_in_file(func):
        def wrapper(*args: list[Any], **kwargs: dict[Any:Any]):
            try:
                logger.info(f"Запуск функции {func.__name__}")
                result = func(*args, **kwargs)
            except Exception as ex:
                logger.error(f"Произошла ошибка {ex} во время выполнения функции {func.__name__}")
                result = ""

            try:
                logger.info(f"Запись данных функции {func.__name__} в файл {path}")
                with open(path, "a", encoding="UTF-8") as file:
                    file.write(f"{func.__name__}: {result}\n\n")
            except Exception as ex:
                logger.error(f"Произошла ошибка {ex} во время записи в файл данных функции {func.__name__}")
                result = ""

            return result

        return wrapper

    logger.info("Завершение работы функции логирования в файл\n")

    return write_in_file


@log_to_file()
def expenses_by_category(
    df: pd.DataFrame,
    category_name: str,
    optional_date: str = datetime.datetime.isoformat(datetime.datetime.now(), sep=" "),
) -> str:
    """Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)"""

    starting_date = datetime.datetime.strptime(optional_date[:19], "%Y-%m-%d %H:%M:%S")
    ending_date = datetime.datetime.strptime(optional_date[:19], "%Y-%m-%d %H:%M:%S")

    suitable_transactions = []

    for i in range(0, 3):
        days_in_month = calendar.monthrange(ending_date.year, ending_date.month)[1]
        ending_date -= datetime.timedelta(days=days_in_month)

    try:
        logger.info("Начали фильтрацию данных по заданным критериям функцией 'expenses_by_category'")
        for index, row in df.iterrows():
            transaction_date = datetime.datetime.strptime(df.loc[index, "Дата операции"], "%d.%m.%Y %H:%M:%S")

            if ending_date < transaction_date < starting_date:
                if df.loc[index, "Категория"] == category_name:
                    if df.loc[index, "Сумма операции"] < 0:
                        suitable_transactions.append(row.to_dict())
    except Exception as ex:
        logger.error(f"Произошла ошибка {ex} функции 'expenses_by_category'")
        suitable_transactions = []

    json_answer = json.dumps(suitable_transactions, ensure_ascii=False, indent=4)

    logger.info("Завершение работы функции 'expenses_by_category'\n")

    return json_answer


@log_to_file()
def spending_by_weekday(
    df: pd.DataFrame, optional_date: str = datetime.datetime.isoformat(datetime.datetime.now(), sep=" ")
) -> str:
    """Функция возвращает средние траты в каждый из дней недели за последние три месяца (от переданной даты)"""

    starting_date = datetime.datetime.strptime(optional_date[:19], "%Y-%m-%d %H:%M:%S")
    ending_date = datetime.datetime.strptime(optional_date[:19], "%Y-%m-%d %H:%M:%S")

    for i in range(0, 3):
        days_in_month = calendar.monthrange(ending_date.year, ending_date.month)[1]
        ending_date -= datetime.timedelta(days=days_in_month)

    amount_of_days_of_the_week = [{0: 0}, {1: 0}, {2: 0}, {3: 0}, {4: 0}, {5: 0}, {6: 0}]  # траты в каждый из дней
    counter_dict = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}  # кол-во трат в каждый из дней недели

    try:
        logger.info("Начали фильтрацию данных по заданным критериям функцией 'spending_by_weekday'")
        for i in df.index:
            transaction_date = datetime.datetime.strptime(df.loc[i, "Дата операции"], "%d.%m.%Y %H:%M:%S")

            if ending_date < transaction_date < starting_date:
                if df.loc[i, "Сумма операции"] < 0:
                    actual_day_of_the_week = datetime.datetime.weekday(transaction_date)

                    for day in amount_of_days_of_the_week:
                        for key in day.keys():
                            if key == actual_day_of_the_week:
                                day.update({key: day[key] + df.loc[i, "Сумма операции"].item()})
                                counter_dict.update({key: counter_dict[key] + 1})
    except Exception as ex:
        logger.error(f"Произошла ошибка {ex} функции 'spending_by_weekday'")

    for el in counter_dict:
        if counter_dict[el] == 0:
            counter_dict[el] = -1

    average_spending = [
        {
            "Понедельник": -round(amount_of_days_of_the_week[0][0] / counter_dict[0], 2),
            "Вторник": -round(amount_of_days_of_the_week[1][1] / counter_dict[1], 2),
            "Среда": -round(amount_of_days_of_the_week[2][2] / counter_dict[2], 2),
            "Четверг": -round(amount_of_days_of_the_week[3][3] / counter_dict[3], 2),
            "Пятница": -round(amount_of_days_of_the_week[4][4] / counter_dict[4], 2),
            "Суббота": -round(amount_of_days_of_the_week[5][5] / counter_dict[5], 2),
            "Воскресенье": -round(amount_of_days_of_the_week[6][6] / counter_dict[6], 2),
        }
    ]  # средние траты в каждый из дней недели

    json_answer = json.dumps(average_spending, ensure_ascii=False, indent=4)

    logger.info("Завершение работы функции 'spending_by_weekday'\n")

    return json_answer


@log_to_file()
def spending_of_wor_or_wee_days(
    df: pd.DataFrame, optional_date: str = datetime.datetime.isoformat(datetime.datetime.now(), sep=" ")
) -> str:
    """Функция выводит средние траты в рабочие и в выходные дни за последние три месяца (от переданной даты)"""

    starting_date = datetime.datetime.strptime(optional_date[:19], "%Y-%m-%d %H:%M:%S")
    ending_date = datetime.datetime.strptime(optional_date[:19], "%Y-%m-%d %H:%M:%S")

    for i in range(0, 3):
        days_in_month = calendar.monthrange(ending_date.year, ending_date.month)[1]
        ending_date -= datetime.timedelta(days=days_in_month)

    workdays_list = {"amount": 0, "counter": 0}  # количество и счетчик трат в рабочие дни
    weekdays_list = {"amount": 0, "counter": 0}  # количество и счетчик трат в выходные дни

    try:
        logger.info("Начали фильтрацию данных по заданным критериям функцией 'spending_of_wor_or_wee_days'")
        for i in df.index:
            transaction_date = datetime.datetime.strptime(df.loc[i, "Дата операции"], "%d.%m.%Y %H:%M:%S")

            if ending_date < transaction_date < starting_date:
                if df.loc[i, "Сумма операции"] < 0:
                    actual_day_of_the_week = datetime.datetime.weekday(transaction_date)

                    if actual_day_of_the_week < 5:
                        workdays_list.update(
                            {
                                "amount": workdays_list["amount"] + df.loc[i, "Сумма операции"].item(),
                                "counter": workdays_list["counter"] + 1,
                            }
                        )
                    else:
                        weekdays_list.update(
                            {
                                "amount": weekdays_list["amount"] + df.loc[i, "Сумма операции"].item(),
                                "counter": weekdays_list["counter"] + 1,
                            }
                        )
    except Exception as ex:
        logger.error(f"Произошла ошибка {ex} функции 'spending_of_wor_or_wee_days'")

    for el in workdays_list:
        if workdays_list[el] == 0:
            workdays_list[el] = -1

    average_spending = [
        {
            "workdays": -round(workdays_list["amount"] / workdays_list["counter"], 2),
            "weekdays": -round(weekdays_list["amount"] / weekdays_list["counter"], 2),
        }
    ]  # средние траты в рабочие и выходные дни

    json_answer = json.dumps(average_spending, ensure_ascii=False, indent=4)

    logger.info("Завершение работы функции 'spending_of_wor_or_wee_days'\n")

    return json_answer
