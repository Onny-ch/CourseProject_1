import datetime
import logging
import os
import time
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
currency_api = os.getenv("API_KEY1")
stocks_api = os.getenv("API_KEY2")

logger = logging.getLogger("utils")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("logs/utils.log", encoding="UTF-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def read_xls(xls_file: str) -> list[Any]:
    """Функция считывания финансовых операций из Excel файла"""

    try:
        logger.info("Чтение xls файла\n")
        df = pd.read_excel(xls_file)
        transactions_data = df.to_dict(orient="records")
    except Exception as ex:
        logger.error(f"Произошла ошибка {ex} функции 'read_xls'")
        transactions_data = []

    logger.info("Завершение работы функции 'read_xls'\n")

    return transactions_data


def greetings(time_string: str) -> str:
    """Функция приветствия пользователя, меняющаяся от времени суток"""

    greetings_string = ""
    ttt = time.strptime(time_string, "%Y-%m-%d %H:%M:%S")

    try:
        logger.info("Определение времени суток функцией 'greetings'")
        if 6 <= ttt[3] < 10:
            greetings_string = "Доброе утро"
        elif 10 <= ttt[3] < 17:
            greetings_string = "Добрый день"
        elif 17 <= ttt[3] < 22:
            greetings_string = "Добрый вечер"
        elif 22 <= ttt[3] < 24 or 00 <= ttt[3] < 6:
            greetings_string = "Доброй ночи"
    except Exception as ex:
        logger.error(f"Произошла ошибка {ex} функции 'greetings'")

    logger.info("Завершение работы функции 'greetings'\n")

    return greetings_string


def card_information(transactions_data: list[dict[Any, Any]]) -> list[dict[str, Any]]:
    """
    Информация по каждой карте:
        1. Последние 4 цифры карты,
        2. Общая сумма расходов,
        3. Кэшбек (1 рубль на каждые 100 рублей)
    """

    expenses_amount = list()
    card_numbers = list()

    try:
        logger.info("Поиск номеров карт по транзакциям функции 'card_information'")
        for transaction in transactions_data:
            if type(transaction["Номер карты"]) is str:
                if transaction["Номер карты"] not in card_numbers:
                    card_numbers.append(transaction["Номер карты"])
    except Exception as ex:
        logger.error(f"Произошла ошибка {ex} функции 'card_information' во время поиска номеров карт")

    try:
        logger.info("Сборка списка данных по картам функцией 'card_information'")
        for card in card_numbers:
            total_spent = float()
            cashback = float()
            for transaction in transactions_data:
                if card is transaction["Номер карты"]:
                    if int(transaction["Сумма операции"]) < 0:
                        total_spent += float(transaction["Сумма операции"])
                        cashback += float(transaction["Сумма операции"]) / 100
            expenses_amount.append(
                {"last_digits": card[1:], "total_spent": round(total_spent, 1), "cashback": -round(cashback, 1)}
            )
    except Exception as ex:
        logger.error(f"Произошла ошибка {ex} функции 'card information' во время сборки списка данных по картам")

    logger.info("Завершение работы функции 'information'\n")

    return expenses_amount


def top_five_by_trans_amount(transactions_date: str, transactions_data: list[dict[Any, Any]]) -> list[dict[Any, Any]]:
    """
    Сортировка списка транзакций по 'Сумме платежа' и возврат 5 самых дорогих в виде:
        {
        "date": "21.12.2021",
        "amount": 1198.23,
        "category": "Переводы",
        "description": "Перевод Кредитная карта. ТП 10.2 RUR"      2020-12-17 05:00:00
        }
    """

    sorted_transactions_by_time = []
    actual_data = []

    start_month_date = time.strptime(f"{transactions_date[:8]}01{transactions_date[10:]}", "%Y-%m-%d %H:%M:%S")
    actual_date = time.strptime(transactions_date, "%Y-%m-%d %H:%M:%S")

    try:
        logger.info("Поиск и сортировка списка транзакций по сумме платежа функцией 'top_five_by_trans_amount'")
        for transaction in transactions_data:
            transaction_date = time.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S")

            if actual_date > transaction_date > start_month_date:
                actual_data.append(transaction)

        sorted_data = sorted(actual_data, key=lambda x: x["Сумма платежа"])
    except Exception as ex:
        logger.error(f"Произошла ошибка {ex} функции 'top_five_by_trans_amount'")
        sorted_data = []

    try:
        logger.info("Сборка топ пяти транзакций функцией 'top_five_by_trans_amount'")
        for transaction in sorted_data[:5]:
            sorted_transactions_by_time.append(
                {
                    "date": transaction["Дата операции"][:10],
                    "amount": transaction["Сумма операции"],
                    "category": transaction["Категория"],
                    "description": transaction["Описание"],
                }
            )
    except Exception as ex:
        logger.error(f"Произошла ошибка {ex} функции 'top_five_by_trans_amount'")

    logger.info("Завершение работы функции 'top_five_by_trans_amount'\n")

    return sorted_transactions_by_time


def expenses_calculator(df: pd.DataFrame, transactions_date: str, date_range: str = "M") -> dict[Any, Any]:
    """Расчет всех расходов в заданном диапазоне (неделя, месяц, год или за все время"""

    actual_date_time = time.strptime(transactions_date, "%Y-%m-%d %H:%M:%S")

    actual_date_datetime = datetime.datetime.strptime(transactions_date, "%Y-%m-%d %H:%M:%S")

    range_date_datetime = datetime.datetime.strptime(transactions_date, "%Y-%m-%d %H:%M:%S")

    try:
        logger.info("Определение временного диапазона для расчета расходов функцией 'expenses_calculator'")
        if date_range == "W":
            range_date_datetime = range_date_datetime - datetime.timedelta(days=actual_date_time.tm_wday)
            range_date_datetime = range_date_datetime.replace(hour=0, minute=0, second=0)

        elif date_range == "M":
            range_date_datetime = range_date_datetime.replace(day=1, hour=0, minute=0, second=0)

        elif date_range == "Y":
            range_date_datetime = range_date_datetime.replace(month=1, day=1, hour=0, minute=0, second=0)

        elif date_range == "ALL":
            range_date_datetime = range_date_datetime.replace(year=1970, month=1, day=1, hour=0, minute=0, second=0)

    except Exception as ex:
        logger.error(f"Произошла ошибка {ex} функции 'expenses_calculator'")

    amount = 0

    category_list: list[dict[str, Any]] = []

    nan_check_summ = df["Сумма операции"].notnull()
    nan_check_cat = df["Категория"].notnull()

    try:
        logger.info("Поиск и сборка транзакций в временном диапазоне функцией 'expenses_calculator'")
        for i in df.index:
            datetime_for_i = datetime.datetime.strptime(df.loc[i, "Дата операции"], "%d.%m.%Y %H:%M:%S")

            if range_date_datetime < datetime_for_i < actual_date_datetime:
                if df.loc[i, "Сумма операции"] < 0:
                    amount += df.loc[i, "Сумма операции"].item()

                    if nan_check_summ[i] and nan_check_cat[i]:

                        found = False

                        for cat in category_list:
                            if df.loc[i, "Категория"] == cat["category"]:
                                cat["amount"] += df.loc[i, "Сумма операции"].item()
                                found = True
                                break

                        if not found:
                            category_list.append(
                                {"category": df.loc[i, "Категория"], "amount": df.loc[i, "Сумма операции"].item()}
                            )

                    else:
                        found = False

                        for cat in category_list:
                            if cat["category"] == "Остальное":
                                cat["amount"] += df.loc[i, "Сумма операции"].item()
                                found = True
                                break

                        if not found:
                            category_list.append(
                                {"category": "Остальное", "amount": df.loc[i, "Сумма операции"].item()}
                            )
    except Exception as ex:
        logger.error(f"Произошла ошибка {ex} функции 'expenses_calculator'")

    total_amount = round(amount, 2)

    transfers_and_cash = []
    to_remove = []

    category_other = dict()

    for el in category_list:
        if el["category"] == "Наличные" or el["category"] == "Переводы":
            el["amount"] = round(el["amount"], 2)
            transfers_and_cash.append(el)
            to_remove.append(el)

        elif el["category"] == "Остальное":
            el["amount"] = round(el["amount"], 2)
            category_other = el
            category_list.remove(el)

    for el in to_remove:
        category_list.remove(el)

    category_list.sort(key=lambda x: x["amount"])

    main = []

    for elem in category_list[:7]:
        main.append({"category": elem["category"], "amount": round(elem["amount"], 2)})

    main.append(category_other)

    try:
        logger.info("Получение элемента категории 'Переводы' функцией 'expenses_calculator'")
        transfers = next(el["amount"] for el in transfers_and_cash if el["category"] == "Переводы")
    except StopIteration as ex:
        logger.error(f"Произошла ошибка {ex} при попытке получения элемента категории 'Переводы'")
        transfers = 0

    try:
        logger.info("Получение элемента категории 'Наличные' функцией 'expenses_calculator'")
        cash = next(el["amount"] for el in transfers_and_cash if el["category"] == "Наличные")
    except StopIteration as ex:
        logger.error(f"Произошла ошибка {ex} при попытке получения элемента категории 'Наличные'")
        cash = 0

    expenses = {
        "total_amount": total_amount,
        "main": main,
        "transfers_and_cash": [
            {
                "category": "Наличные",
                "amount": cash,
            },
            {
                "category": "Переводы",
                "amount": transfers,
            },
        ],
    }

    logger.info("Завершение работы функции 'expenses_calculator'\n")

    return expenses


def income_calculator(df: pd.DataFrame, transactions_date: str, date_range: str = "M") -> dict[Any, Any]:
    """Расчет всех приходов в заданном диапазоне (неделя, месяц, год или за все время"""

    actual_date_time = time.strptime(transactions_date, "%Y-%m-%d %H:%M:%S")
    actual_date_datetime = datetime.datetime.strptime(transactions_date, "%Y-%m-%d %H:%M:%S")
    range_date_datetime = datetime.datetime.strptime(transactions_date, "%Y-%m-%d %H:%M:%S")

    try:
        logger.info("Определение временного диапазона для расчета расходов функцией 'income_calculator'")
        if date_range == "W":
            range_date_datetime = range_date_datetime - datetime.timedelta(days=actual_date_time.tm_wday)
            range_date_datetime = range_date_datetime.replace(hour=0, minute=0, second=0)

        elif date_range == "M":
            range_date_datetime = range_date_datetime.replace(day=1, hour=0, minute=0, second=0)

        elif date_range == "Y":
            range_date_datetime = range_date_datetime.replace(month=1, day=1, hour=0, minute=0, second=0)

        elif date_range == "ALL":
            range_date_datetime = range_date_datetime.replace(year=1970, month=1, day=1, hour=0, minute=0, second=0)

    except Exception as ex:
        logger.error(f"Произошла ошибка {ex} функции 'income_calculator'")

    amount = 0

    category_list: list[dict[str, Any]] = []

    nan_check_summ = df["Сумма операции"].notnull()
    nan_check_cat = df["Категория"].notnull()

    try:
        logger.info("Поиск и сборка транзакций в временном диапазоне функцией 'income_calculator'")
        for i in df.index:
            datetime_for_i = datetime.datetime.strptime(df.loc[i, "Дата операции"], "%d.%m.%Y %H:%M:%S")

            if range_date_datetime < datetime_for_i < actual_date_datetime:
                if df.loc[i, "Сумма операции"] > 0:
                    amount += df.loc[i, "Сумма операции"].item()

                    if nan_check_summ[i] and nan_check_cat[i]:

                        found = False

                        for cat in category_list:
                            if df.loc[i, "Категория"] == cat["category"]:
                                cat["amount"] += df.loc[i, "Сумма операции"].item()
                                found = True
                                break

                        if not found:
                            category_list.append(
                                {"category": df.loc[i, "Категория"], "amount": df.loc[i, "Сумма операции"].item()}
                            )

                    else:
                        found = False

                        for cat in category_list:
                            if cat["category"] == "Остальное":
                                cat["amount"] += df.loc[i, "Сумма операции"].item()
                                found = True
                                break

                        if not found:
                            category_list.append(
                                {"category": "Остальное", "amount": df.loc[i, "Сумма операции"].item()}
                            )
    except Exception as ex:
        logger.error(f"Произошла ошибка {ex} функции 'income_calculator' при сборке списка 'category_list'")

    total_amount = round(amount, 2)

    category_list.sort(key=lambda x: x["amount"], reverse=True)

    income = {
        "total_amount": total_amount,
        "main": category_list,
    }

    logger.info("Завершение работы функции 'income_calculator'\n")

    return income


def exchange_rate(user_data: dict[str, list[str]]) -> list[dict[str, float]]:
    """Информация по курсу валют"""

    url = "https://api.apilayer.com/currency_data/live"

    headers = {
        "apikey": currency_api,
    }

    params = {
        "source": "RUB",
    }

    currency_request = requests.get(url, headers=headers, params=params)

    json_currency_data = currency_request.json()

    currency_list = []

    try:
        logger.info("")
        for currency in user_data["user_currencies"]:
            currency_list.append(
                {"currency": currency, "rate": round(1 / json_currency_data["quotes"][f"RUB{currency}"], 2)}
            )
    except Exception as ex:
        logger.error(f"Произошла ошибка {ex} функции 'exchange_rate' при попытке сборки списка 'currency_list'")

    logger.info("Завершение работы функции 'exchange_rate'\n")

    return currency_list


def stock_price(user_data: dict[str, list[str]]) -> list[dict[str, str]]:
    """Стоимость акций из S&P500"""

    stock_prices = []

    try:
        logger.info("")
        for symbol in user_data["user_stocks"]:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={stocks_api}"

            request_data = requests.get(url)
            json_stock_data = request_data.json()

            stock_prices.append(
                {
                    "stock": json_stock_data["Global Quote"]["01. symbol"],
                    "price": json_stock_data["Global Quote"]["02. open"],
                }
            )
    except Exception as ex:
        logger.error(f"Произошла ошибка {ex} функции 'stock_price' при попытке сборки списка 'stock_prices'")

    logger.info("Завершение работы функции 'stock_price'\n")

    return stock_prices
