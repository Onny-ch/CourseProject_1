import json
from unittest.mock import patch

from src.utils import read_xls
from src.views import event_page, home_page

file_info = read_xls("data\\operations.xlsx")

with open("user_settings.json", "r") as file:
    user_settings = json.load(file)


def test_home_page():
    with patch("src.views.greetings", return_value="Hi message"), patch(
        "src.views.card_information", return_value="Card info"
    ), patch("src.views.top_five_by_trans_amount", return_value="Top 5 trans"), patch(
        "src.views.exchange_rate", return_value="Values rate"
    ), patch(
        "src.views.stock_price", return_value="Stocks rate"
    ):

        result = home_page(file_info, user_settings, "2021-12-17 05:00:00")

        assert (
            result
            == """{
    "greetings": "Hi message",
    "cards": "Card info",
    "top_transactions": "Top 5 trans",
    "currency_rates": "Values rate",
    "stock_prices": "Stocks rate"
}"""
        )


def test_event_page():
    with patch(
        "src.views.expenses_calculator",
        return_value={
            "total_amount": -11,
            "main": "No main expenses",
            "transfers_and_cash": "Without transfers and cash",
        },
    ):
        with patch("src.views.income_calculator", return_value={"total_amount": 11, "main": "No main income"}):
            with patch("src.views.exchange_rate", return_value="Values rate"):
                with patch("src.views.stock_price", return_value="Stocks rate"):
                    result = event_page(file_info, user_settings, "2020-12-17 05:00:00")

                    assert (
                        result
                        == """{
    "expenses": {
        "total amount": -11,
        "main": "No main expenses",
        "transfers_and_cash": "Without transfers and cash"
    },
    "income": {
        "total_amount": 11,
        "main": "No main income"
    },
    "currency_rates": "Values rate",
    "stock_prices": "Stocks rate"
}"""
                    )
