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


def download_par_yield_csv(year: int) -> str:
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


def refresh_data_for_new_year():
    if f"{datetime.now().year}.csv" not in os.listdir(DATA_DIR):
        try:
            text: str = download_par_yield_csv(datetime.now().year)
            with open(DATA_DIR / f"{year}.csv", "w") as f:
                f.write(text)

        except Exception as e:
            logger.error("Error:", e)


def get_stored_data(year: int) -> List[List[str]]:
    with open(DATA_DIR / f"{year}.csv", "r") as file:
        reader = csv.reader(file)
        return list(reader)  # assumes small file, fine to read into memory


def get_most_recent_year_with_data_stored():
    return max(int(filename.removesuffix(".csv")) for filename in os.listdir(DATA_DIR))


def refresh_data_for_new_weekday(year):
    data = get_stored_data(year)
    date_str = data[1][0]
    month_str, day_str, year_str = date_str[:2], date_str[3:5], date_str[6:]
    most_recent_day_with_data = f"20{year_str}{month_str}{day_str}"
    most_recent_weekday = get_most_recent_weekday().strftime("%Y%m%d")
    if most_recent_day_with_data != most_recent_weekday:
        text: str = download_par_yield_csv(year)
        with open(DATA_DIR / f"{year}.csv", "w") as f:
            f.write(text)
