import datetime
import json
import logging
import math
import re
from typing import Any

import pandas as pd

logger = logging.getLogger("services")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("logs/services.log", encoding="UTF-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def best_cashback_categories(file_info: pd.DataFrame, year: str, month: str) -> str:
    """
    Функция позволяет проанализировать, какие категории были наиболее выгодными
    для выбора в качестве категорий повышенного кэшбека
    """

    category_list: list[dict[Any, Any]] = []

    nan_check_cashback = file_info["Кэшбэк"].notnull()

    year_datetime = datetime.datetime.strptime(f"{year}.{month}", "%Y.%m")

    if month == "12":
        year_datetime_range = datetime.datetime.strptime(f"{int(year) + 1}.01", "%Y.%m")
        year_datetime_range = year_datetime_range - datetime.timedelta(seconds=1)
    else:
        year_datetime_range = datetime.datetime.strptime(f"{year}.{int(month)+1}", "%Y.%m")
        year_datetime_range = year_datetime_range - datetime.timedelta(seconds=1)

    try:
        logger.info("Начали фильтрацию транзакций функцией 'best_cashback_categories'")
        for i in file_info.index:
            trans_datetime = datetime.datetime.strptime(file_info.loc[i, "Дата операции"], "%d.%m.%Y %H:%M:%S")

            if year_datetime < trans_datetime < year_datetime_range:
                if nan_check_cashback[i]:
                    found = False

                    for eel in category_list:
                        if file_info.loc[i, "Категория"] == eel["Категория"]:
                            eel["Кэшбэк"] += file_info.loc[i, "Кэшбэк"].item()

                            found = True

                    if not found:
                        category_list.append(
                            {"Категория": file_info.loc[i, "Категория"], "Кэшбэк": file_info.loc[i, "Кэшбэк"].item()}
                        )
    except Exception as ex:
        logger.error(f"Произошла ошибка {ex} функции 'best_cashback_categories'")
        category_list = []

    sorted_category_list = sorted(category_list, key=lambda x: x["Кэшбэк"], reverse=True)

    cashback_categories = {}

    logger.info("Начали сбор топовых категорий из отфильтрованных транзакций функции 'best_cashback_categories'")
    for i in range(0, 3):
        try:
            cashback_categories.update(
                {
                    sorted_category_list[i]["Категория"]: sorted_category_list[i]["Кэшбэк"],
                }
            )
        except IndexError as ex:
            logger.error(f"Произошла ошибка {ex} функции 'best_cashback_categories'")
            pass

    json_cashback_categories = json.dumps(cashback_categories, ensure_ascii=False, indent=4)

    logger.info("Завершение работы функции 'best_cashback_categories'\n")

    return json_cashback_categories


def investment_bank(year_month: str, transactions: list[dict[str, Any]], limit: int = 50) -> float:
    """Функция, высчитывающая сумму денег, которую удалось бы отложить в 'Инвесткопилку'"""

    month_datetime = datetime.datetime.strptime(year_month, "%Y-%m")

    if year_month[-2:] == "12":
        month_datetime_range = datetime.datetime.strptime(f"{int(year_month[0:4]) + 1}.01", "%Y.%m")
        month_datetime_range = month_datetime_range - datetime.timedelta(seconds=1)
    else:
        month_datetime_range = datetime.datetime.strptime(f"{year_month[0:4]}.{int(year_month[-2:])+1}", "%Y.%m")
        month_datetime_range = month_datetime_range - datetime.timedelta(seconds=1)

    total_invest = 0

    try:
        logger.info("Работа функции высчитывания суммы денег, которую получили бы с Инвесткопилки")
        for el in transactions:
            trans_datetime = datetime.datetime.strptime(el["Дата операции"], "%d.%m.%Y %H:%M:%S")

            if month_datetime < trans_datetime < month_datetime_range:
                if el["Сумма операции"] < 0:
                    difference = math.ceil(-el["Сумма операции"] / limit) * limit
                    total_invest += difference + el["Сумма операции"]
    except Exception as ex:
        logger.info(f"Произошла ошибка {ex} функции 'investment_bank'")

    logger.info("Завершение работы функции 'investment_bank'\n")

    return round(total_invest, 2)


def simple_search(transactions: list[dict[str, Any]], search_string: str) -> str:
    """Функция, производящая поиск по запросу среди транзакций, содержащих запрос в описании или категории."""

    searched_transactions: list[dict[Any, Any]] = []

    try:
        logger.info("Работа функции поиска по запросу 'simple_search'")
        for el in transactions:
            if not pd.isna(el["Категория"]):
                if search_string.lower() in el["Описание"].lower() or search_string.lower() in el["Категория"].lower():
                    searched_transactions.append(el)
    except Exception as ex:
        logger.error(f"Произошла ошибка {ex} функции 'simple_search'")

    json_answer = json.dumps(searched_transactions, ensure_ascii=False, indent=4)

    logger.info("Завершение работы функции 'simple_search'\n")

    return json_answer


def phone_number_search(transactions: list[dict[str, Any]]) -> str:
    """Функция возвращает JSON со всеми транзакциями, содержащими в описании мобильные номера."""

    all_transactions: list[dict[Any, Any]] = []

    pattern = re.compile(r"\d{3} \d\d-\d\d-\d\d")

    try:
        logger.info("Работа функции фильтрации транзакций по наличию мобильных номеров 'phone_number_search'")
        for el in transactions:
            if re.search(pattern, el["Описание"]):
                all_transactions.append(el)
    except Exception as ex:
        logger.error(f"Произошла ошибка {ex} функции 'phone_number_search'")

    json_answer = json.dumps(all_transactions, ensure_ascii=False, indent=4)

    logger.info("Завершение работы функции 'phone_number_search'\n")

    return json_answer


def search_for_transfers_to_individuals(transactions: list[dict[str, Any]]) -> str:
    """Функция возвращает JSON со всеми транзакциями, которые относятся к переводам физлицам."""

    pattern = re.compile(r"\w+ \w\.")

    try:
        logger.info("Работа функции фильтрации транзакций и нахождения относящихся к переводам физлицам")
        list_of_transfers: list[dict[Any, Any]] = [
            elem
            for elem in transactions
            if elem["Категория"] == "Переводы" and pattern.search(elem["Описание"], re.IGNORECASE)
        ]
    except Exception as ex:
        logger.error(f"Произошла ошибка {ex} функции 'search_for_transfers_to_individuals'")
        list_of_transfers = []

    json_with_cat = json.dumps(list_of_transfers, ensure_ascii=False, indent=4)

    logger.info("Завершение работы функции 'search_for_transfers_to_individuals'\n")

    return json_with_cat
