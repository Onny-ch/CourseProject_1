import json
import logging

from src.utils import (
    card_information,
    exchange_rate,
    expenses_calculator,
    greetings,
    income_calculator,
    stock_price,
    top_five_by_trans_amount,
)

logger = logging.getLogger("views")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("logs/views.log", encoding="UTF-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


# Функция для страницы "Главная"
def home_page(file, user_data, date_time_string: str) -> str:  # готова
    """
    Принимает строку с датой и возвращает информацию в виде:
        1. Приветствие в соответствии с временем суток
        2. Общую информацию по каждой карте
        3. Топ-5 транзакций по сумме платежа
        4. Курс валют
        5. Стоимость акций из S&p500
    """

    greet_string, card_info, top_5, rate, stocks_prices = str(), str(), str(), str(), str()
    try:
        logger.info("Начало выполнения функции из utils.py, сбор данных для JSON строки страницы Главная")

        greet_string = greetings(date_time_string)  # 1 Приветствие

        card_info = card_information(file)  # 2 Инфо по карте

        top_5 = top_five_by_trans_amount(date_time_string, file)  # 3 Топ 5 по сумме транзакций

        rate = exchange_rate(user_data)  # 4 Курс валют

        stocks_prices = stock_price(user_data)  # 5 Стоимость акций

    except Exception as ex:
        logger.error(f"Произошла ошибка {ex}")

    try:
        logger.info("Сборка JSON'а с данными для страницы Главная функцией 'home_page'")
        home_page_answer = {
            "greetings": greet_string,
            "cards": card_info,
            "top_transactions": top_5,
            "currency_rates": rate,
            "stock_prices": stocks_prices,
        }
    except Exception as ex:
        logger.error(f"Произошла ошибка {ex} функции 'home_page'")
        home_page_answer = {}

    json_home_page = json.dumps(home_page_answer, ensure_ascii=False, indent=4)

    logger.info("Завершение работы функции 'home_page'\n")

    return json_home_page


def event_page(file, user_data, actual_date_string: str, date_range: str = "M") -> str:
    """
    Принимает на вход дату и параметр диапазона, на выходе выдавая:
        1. Расходы
        2. Поступления
        3. Курс валют
        4. Стоимость акций из S&P 500
    """

    try:
        logger.info("Начинаем выполнять функции из utils.py, чтобы собрать данные для JSON строки страницы События")

        expenses = expenses_calculator(file, actual_date_string, date_range)  # 1. Расходы

        income = income_calculator(file, actual_date_string, date_range)  # 2. Поступления

        rate = exchange_rate(user_data)  # 3. Курс валют

        stock_prices = stock_price(user_data)  # 4. Стоимость акций

    except Exception as ex:
        logger.error(f"Произошла ошибка {ex}")
        expenses = {}
        income = {}
        rate = []
        stock_prices = []

    try:
        logger.info("Сборка JSON'а с данными для страницы События")
        event_page_answer = {
            "expenses": {
                "total amount": expenses["total_amount"],
                "main": expenses["main"],
                "transfers_and_cash": expenses["transfers_and_cash"],
            },
            "income": {"total_amount": income["total_amount"], "main": income["main"]},
            "currency_rates": rate,
            "stock_prices": stock_prices,
        }
    except Exception as ex:
        logger.error(f"Произошла ошибка {ex} функции 'event_page'")
        event_page_answer = {}

    json_event_page = json.dumps(event_page_answer, ensure_ascii=False, indent=4)

    logger.info("Завершение работы функции 'event_page'\n")

    return json_event_page
