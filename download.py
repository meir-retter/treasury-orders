import csv
from typing import List
import requests
from datetime import datetime, timedelta
from pathlib import Path
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


DATA_DIR = Path("./data")
BASE_URL = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv"


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_csv_download_url(year: int):
    return f"{BASE_URL}/{year}/all?field_tdr_date_value={year}&type=daily_treasury_yield_curve&page&_format=csv"


def get_most_recent_weekday() -> datetime:
    today = datetime.today()
    if today.weekday() == 5:  # Saturday
        return today - timedelta(days=1)
    elif today.weekday() == 6:  # Sunday
        return today - timedelta(days=2)
    return today


def download_csv(year: int) -> str:
    ensure_data_dir()
    try:
        with requests.Session() as s:
            download = s.get(get_csv_download_url(year))
            download.raise_for_status()
            file_text: str = download.content.decode("utf-8")
            return file_text
    except Exception as e:
        logger.error(f"ERROR, failed to download data for {year}: {e}")
        return ""


def try_downloading_csv_for_current_year():
    try:
        text: str = download_csv(datetime.now().year)
        if text:
            with open(DATA_DIR / f"{year}.csv", "w") as f:
                f.write(text)
    except Exception as e:
        logger.error("Error:", e)


def read_downloaded_csv(year: int) -> List[List[str]]:
    with open(DATA_DIR / f"{year}.csv", "r") as file:
        reader = csv.reader(file)
        return list(reader)  # assumes small file, fine to read into memory


def get_most_recent_year_with_csv_downloaded():
    return max(int(filename.removesuffix(".csv")) for filename in os.listdir(DATA_DIR))


def csv_row_exists_for_most_recent_weekday(current_business_year: int) -> bool:
    data = read_downloaded_csv(current_business_year)
    date_str = data[1][0]
    month_str, day_str, year_str = date_str[:2], date_str[3:5], date_str[6:]
    most_recent_day_with_data = f"{year_str}{month_str}{day_str}"
    most_recent_weekday = get_most_recent_weekday().strftime("%Y%m%d")
    print(most_recent_weekday)
    print(most_recent_day_with_data)
    return most_recent_day_with_data == most_recent_weekday


def get_yield_curve_data_for_this_year():
    print(1)
    current_year = datetime.now().year
    csv_already_downloaded_for_current_year: bool = f"{current_year}.csv" in os.listdir(
        DATA_DIR
    )
    if csv_already_downloaded_for_current_year:
        current_business_year = current_year
    else:
        try_downloading_csv_for_current_year()
        print(2)
        current_business_year = get_most_recent_year_with_csv_downloaded()
        print(3)
        # current_business_year is usually the current year
        # but could be the previous year e.g. if right now it's Saturday Jan 1
        # TODO handle case where the app sits for a full year unused, leaving a data gap
        # would prefer to not download more often than needed because it's slow
    print(current_business_year)
    print(4)
    if not csv_row_exists_for_most_recent_weekday(current_business_year):
        print(5)
        new_csv: str = download_csv(current_business_year)
        with open(DATA_DIR / f"{current_business_year}.csv", "w") as f:
            print(6)
            f.write(new_csv)
    print(7)
    return read_downloaded_csv(current_business_year)
