# This is the full list of maturity terms for treasury par yield curve rates as of 2025
# https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2025
# Previous years have had a subset of these
from typing import TypeAlias

Term: TypeAlias = str

MATURITY_TERMS = [
    "1 Mo",
    "1.5 Mo",
    "2 Mo",
    "3 Mo",
    "4 Mo",
    "6 Mo",
    "1 Yr",
    "2 Yr",
    "3 Yr",
    "5 Yr",
    "7 Yr",
    "10 Yr",
    "20 Yr",
    "30 Yr",
]
