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


def ensure_data_dir() -> None:
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


def try_downloading_csv_for_current_year() -> bool:
    did_download = False
    current_year = datetime.now().year
    try:
        text: str = download_csv(current_year)
        if text:
            logger.info(f"Downloaded csv for{datetime.now().year}")
            with open(DATA_DIR / f"{current_year}.csv", "w") as f:
                f.write(text)
            did_download = True
    except Exception as e:
        logger.error("Error:", e)
    return did_download


def read_downloaded_csv(year: int) -> List[List[str]]:
    with open(DATA_DIR / f"{year}.csv", "r") as file:
        reader = csv.reader(file)
        return list(reader)  # assumes small file, fine to read into memory


def get_most_recent_year_with_csv_downloaded() -> int:
    return max(int(filename.removesuffix(".csv")) for filename in os.listdir(DATA_DIR))


def is_csv_row_present_for_most_recent_weekday(current_business_year: int) -> bool:
    newest_csv: List[List[str]] = read_downloaded_csv(current_business_year)
    newest_date_in_csv: str = newest_csv[1][0]
    most_recent_weekday: str = get_most_recent_weekday().strftime("%m/%d/%Y")
    return newest_date_in_csv == most_recent_weekday


def csv_downloaded_for_year(year: int) -> bool:
    return f"{year}.csv" in os.listdir(DATA_DIR)


def refresh_data() -> int:
    """
    - Checks current date versus the latest data downloaded
    - Downloads newest data if needed
    - Then returns the latest year for which data is downloaded
    """
    current_year = datetime.now().year
    if csv_downloaded_for_year(current_year):
        current_business_year = current_year
    else:
        _ = try_downloading_csv_for_current_year()
        current_business_year = get_most_recent_year_with_csv_downloaded()
        # current_business_year is usually the current year
        # but could be the previous year e.g. if right now it's Saturday Jan 1
        # TODO handle case where the app sits for a full year unused, leaving a data gap
        # would prefer to not download more often than needed because it's slow
    if not is_csv_row_present_for_most_recent_weekday(current_business_year):
        new_csv: str = download_csv(current_business_year)
        with open(DATA_DIR / f"{current_business_year}.csv", "w") as f:
            f.write(new_csv)
    return current_business_year
