import json
import logging
from unittest.mock import patch

import pandas as pd
import pytest

from src.utils import (card_information, exchange_rate, expenses_calculator, greetings, income_calculator, read_xls,
                       stock_price, top_five_by_trans_amount)

with open("user_settings.json", "r") as file:
    user_settings = json.load(file)


def test_read_xls(xls_file):
    mock_df = pd.DataFrame(xls_file)

    with patch("pandas.read_excel", return_value=mock_df):
        assert read_xls("") == xls_file


def test_read_xls_error(xls_file):
    mock_df = pd.DataFrame(xls_file)
    with patch("pandas.read_excel", return_value=mock_df):
        with pytest.raises(Exception):
            with patch("logging.error") as mock_log_error:
                read_xls(xls_file)
                assert mock_log_error.called


def test_greetings():
    assert greetings("2020-12-17 05:00:00") == "Доброй ночи"
    assert greetings("2020-12-17 08:00:00") == "Доброе утро"
    assert greetings("2020-12-17 13:00:00") == "Добрый день"
    assert greetings("2020-12-17 17:00:00") == "Добрый вечер"


def test_greetings_error():
    with patch("time.strptime", return_value="000"):
        greetings("")
        with pytest.raises(Exception):
            with patch("logging.error") as mock_log_error:
                assert mock_log_error.called


def test_card_information(xls_file):
    assert card_information(xls_file) == [
        {"last_digits": "7197", "total_spent": -99.0, "cashback": 1.0},
        {"last_digits": "2351", "total_spent": -650.0, "cashback": 6.5},
        {"last_digits": "1419", "total_spent": -99.0, "cashback": 1.0},
    ]


def test_top_five_by_trans_amount(xls_file):
    assert top_five_by_trans_amount("2020-12-17 05:00:00", xls_file) == [
        {
            "date": "07.12.2020",
            "amount": -650.0,
            "category": "Фастфуд",
            "description": "Starbucks Coffee",
        },
        {
            "date": "15.12.2020",
            "amount": -99.0,
            "category": "Фастфуд",
            "description": "Granola",
        },
        {
            "date": "02.12.2020",
            "amount": -99.0,
            "category": "Фастфуд",
            "description": "Baggins coffee",
        },
    ]
    assert top_five_by_trans_amount("2021-12-17 05:00:00", xls_file) == []


def test_expenses_calculator_week(xls_file_one):
    df_one = pd.DataFrame(xls_file_one)
    assert expenses_calculator(df_one, "2020-12-17 05:00:00", "W") == {
        "total_amount": -99,
        "main": [{"category": "Фастфуд", "amount": -99.0}, {}],
        "transfers_and_cash": [
            {
                "category": "Наличные",
                "amount": 0,
            },
            {
                "category": "Переводы",
                "amount": 0,
            },
        ],
    }


def test_expenses_calculator_month(xls_file, xls_file_one):
    df = pd.DataFrame(xls_file)
    assert expenses_calculator(df, "2020-12-17 05:00:00") == {
        "total_amount": -848.0,
        "main": [{"category": "Фастфуд", "amount": -848.0}, {}],
        "transfers_and_cash": [
            {
                "category": "Наличные",
                "amount": 0,
            },
            {
                "category": "Переводы",
                "amount": 0,
            },
        ],
    }
    df_one = pd.DataFrame(xls_file_one)
    assert expenses_calculator(df_one, "2020-12-17 05:00:00") == {
        "total_amount": -1757.0,
        "main": [{"category": "Фастфуд", "amount": -99.0}, {"category": "Остальное", "amount": -99.0}],
        "transfers_and_cash": [
            {
                "category": "Наличные",
                "amount": -650.0,
            },
            {
                "category": "Переводы",
                "amount": -909.0,
            },
        ],
    }


def test_expenses_calculator_year(xls_file_one):
    df_one = pd.DataFrame(xls_file_one)
    assert expenses_calculator(df_one, "2020-12-17 05:00:00", "Y") == {
        "total_amount": -1916.0,
        "main": [
            {"category": "ЧикЧирик", "amount": -159.0},
            {"category": "Фастфуд", "amount": -99.0},
            {"category": "Остальное", "amount": -99.0},
        ],
        "transfers_and_cash": [
            {
                "category": "Наличные",
                "amount": -650.0,
            },
            {
                "category": "Переводы",
                "amount": -909.0,
            },
        ],
    }


def test_expenses_calculator_all(xls_file_one):
    df_one = pd.DataFrame(xls_file_one)
    assert expenses_calculator(df_one, "2020-12-17 05:00:00", "ALL") == {
        "total_amount": -1975.0,
        "main": [
            {"category": "ЧикЧирик", "amount": -159.0},
            {"category": "Фастфуд", "amount": -99.0},
            {"category": "Чирик", "amount": -59.0},
            {"category": "Остальное", "amount": -99.0},
        ],
        "transfers_and_cash": [
            {
                "category": "Наличные",
                "amount": -650.0,
            },
            {
                "category": "Переводы",
                "amount": -909.0,
            },
        ],
    }


def test_income_calculator_week(xls_file_two):
    df_two = pd.DataFrame(xls_file_two)
    assert income_calculator(df_two, "2020-12-17 05:00:00", "W") == {
        "total_amount": 99.0,
        "main": [{"category": "Фастфуд", "amount": 99.0}],
    }


def test_income_calculator_month(xls_file_two):
    df_two = pd.DataFrame(xls_file_two)
    assert income_calculator(df_two, "2020-12-17 05:00:00") == {
        "total_amount": 1757,
        "main": [
            {"category": "Переводы", "amount": 909.0},
            {"category": "Наличные", "amount": 650.0},
            {"category": "Фастфуд", "amount": 99.0},
            {"category": "Остальное", "amount": 99.0},
        ],
    }


def test_income_calculator_year(xls_file_two):
    df_two = pd.DataFrame(xls_file_two)
    assert income_calculator(df_two, "2020-12-17 05:00:00", "Y") == {
        "total_amount": 1916,
        "main": [
            {"category": "Переводы", "amount": 909.0},
            {"category": "Наличные", "amount": 650.0},
            {"category": "ЧикЧирик", "amount": 159.0},
            {"category": "Фастфуд", "amount": 99.0},
            {"category": "Остальное", "amount": 99.0},
        ],
    }


def test_income_calculator_all(xls_file_two):
    df_two = pd.DataFrame(xls_file_two)
    assert income_calculator(df_two, "2020-12-17 05:00:00", "ALL") == {
        "total_amount": 1975,
        "main": [
            {"category": "Переводы", "amount": 909.0},
            {"category": "Наличные", "amount": 650.0},
            {"category": "ЧикЧирик", "amount": 159.0},
            {"category": "Фастфуд", "amount": 99.0},
            {"category": "Остальное", "amount": 99.0},
            {"category": "Чирик", "amount": 59.0},
        ],
    }


def test_exchange_rate(exchange_rate_request):
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = exchange_rate_request
        assert exchange_rate(user_settings) == [
            {"currency": "USD", "rate": 99.25},
            {"currency": "EUR", "rate": 103.41},
        ]


def test_exchange_rate_error(exchange_rate_request, caplog):
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = exchange_rate_request
        with caplog.at_level(logging.ERROR):
            exchange_rate(user_settings)


def test_stock_price(stock_price_aapl, stock_price_amzn, stock_price_googl, stock_price_msft, stock_price_tsla):
    with patch("requests.get") as mock_get:
        mock_get.side_effect = [
            stock_price_aapl,
            stock_price_amzn,
            stock_price_googl,
            stock_price_msft,
            stock_price_tsla,
        ]
        result = stock_price(user_settings)
        assert result == [
            {"stock": "AAPL", "price": "234.1200"},
            {"stock": "AMZN", "price": "239.0150"},
            {"stock": "GOOGL", "price": "195.5550"},
            {"stock": "MSFT", "price": "446.6900"},
            {"stock": "TSLA", "price": "395.2100"},
        ]


def test_stock_price_error(stock_price_aapl):
    with patch("requests.get") as mock_get:
        mock_get.side_effect = stock_price_aapl
        with pytest.raises(Exception):
            with patch("logging.error") as mock_log_error:
                stock_price(user_settings)
            assert mock_log_error.called
