import csv
import requests
from datetime import datetime, timedelta
import os


def get_csv_download_url(year: int):
    return f"https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{year}/all?field_tdr_date_value={year}&type=daily_treasury_yield_curve&page&_format=csv"


def get_most_recent_weekday():
    today = datetime.today()
    weekday = today.weekday()
    if weekday == 5:
        delta = timedelta(days=1)
    elif weekday == 6:
        delta = timedelta(days=2)
    else:
        delta = timedelta(days=0)
    return today - delta


def download_csv_and_write_to_file(year: int):
    with requests.Session() as s:
        download = s.get(get_csv_download_url(year))
        decoded_content = download.content.decode("utf-8")
        if len(decoded_content) > 0:
            with open(f"./data/{year}.csv", "w") as f:
                f.write(decoded_content)


def refresh_data_for_new_year():
    current_year = datetime.now().year
    if f"{current_year}.csv" not in os.listdir("./data/"):
        try:
            download_csv_and_write_to_file(current_year)
        except Exception as e:
            print("Error:", e)


def get_stored_data(year):
    with open(f"./data/{year}.csv", "r") as file:
        reader = csv.reader(file)
        lines = [line for line in reader]  # small file, fine to read into memory
    return lines


def get_most_recent_year_with_data_stored():
    return max(int(filename.removesuffix(".csv")) for filename in os.listdir("./data/"))


def refresh_data_for_new_weekday(year):
    data = get_stored_data(year)
    date_str = data[1][0]
    month_str, day_str, year_str = date_str[:2], date_str[3:5], date_str[6:]
    most_recent_day_with_data = f"20{year_str}{month_str}{day_str}"
    most_recent_weekday = get_most_recent_weekday().strftime("%Y%m%d")
    if most_recent_day_with_data != most_recent_weekday:
        download_csv_and_write_to_file(year)
