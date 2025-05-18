from functools import lru_cache
from typing import Dict
from collections import defaultdict
import logging
from datetime import datetime

from load_csv_data import read_downloaded_csv, csv_downloaded_for_year, refresh_data
from data_model import YieldCurve, HistoricalCurve
from terms import Term

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@lru_cache(maxsize=1)
def prepare_current_yield_curve() -> YieldCurve:
    """
    - Prepares the data for the graph on the left
    - This is the most recent business day's yield curve
    """
    yield_curve_file_rows: List[List[str]] = read_downloaded_csv(refresh_data())

    first_line: List[str] = yield_curve_file_rows[0]
    second_line: List[str] = yield_curve_file_rows[1]

    terms: List[Term] = [col.replace("onth", "o") for col in first_line[1:]]
    date_: str = second_line[0]
    yields: List[int] = [int(val.replace(".", "")) for val in second_line[1:]]

    return YieldCurve(date_, terms, yields)


@lru_cache(maxsize=1)
def prepare_historical_curves() -> Dict[Term, HistoricalCurve]:
    """
    - Prepares the data for the graph on the right
    - Returns a dict
    - - the keys are terms, e.g. "7 Yr"
    - - the values are yield timeseries from 1990 to present day
    """
    histories = defaultdict(lambda: HistoricalCurve([], []))
    current_year = datetime.now().year
    for year in range(1990, current_year + 1):
        if not csv_downloaded_for_year(year):
            logger.warning(f"No data for {year}")
            continue
        csv_rows = read_downloaded_csv(year)
        terms: List[Term] = [term.replace("onth", "o") for term in csv_rows[0][1:]]
        for row in reversed(
            csv_rows[1:]
        ):  # reversed to get them in ascending date order
            row_date: str = row[0]
            yield_values: List[int] = [
                (int(x.replace(".", "")) if x else None) for x in row[1:]
            ]
            for term, yield_value in zip(terms, yield_values):
                if yield_value is not None:
                    histories[term].add_data_point(
                        datetime.strptime(row_date, "%m/%d/%Y"), yield_value
                    )
    return histories
