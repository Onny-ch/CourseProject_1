import json

import pandas as pd

from src.reports import expenses_by_category, spending_by_weekday, spending_of_wor_or_wee_days
from src.services import (
    best_cashback_categories,
    investment_bank,
    phone_number_search,
    search_for_transfers_to_individuals,
    simple_search,
)
from src.utils import read_xls
from src.views import event_page, home_page

with open("user_settings.json", "r") as file:
    user_settings = json.load(file)

file_info = read_xls("data\\operations.xlsx")
file_info_pd = pd.read_excel("data\\operations.xlsx")

if __name__ == "__main__":
    # views.py functionality check
    print(home_page(file_info, user_settings, "2020-12-17 05:00:00"))
    print(event_page(file_info_pd, user_settings, "2020-12-17 05:00:00"))

    # services.py functionality check
    print(best_cashback_categories(file_info_pd, "2021", "11"))
    print(investment_bank("2020-02", file_info))
    print(simple_search(file_info, "ДЛЯ БЕРЕЖ"))
    print(phone_number_search(file_info))
    print(search_for_transfers_to_individuals(file_info))

    # reports.py functionality check
    print(expenses_by_category(file_info_pd, "Фастфуд", "2020-02-25 20:22:19"))
    print(spending_by_weekday(file_info_pd, "2019-02-25 20:22:19"))
    print(spending_of_wor_or_wee_days(file_info_pd, "2019-02-25 20:22:19"))
