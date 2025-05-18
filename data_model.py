from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, List, Literal

from terms import MATURITY_TERMS
from utils import deci_string


@dataclass
class Order:
    """Represents an item in the Previous Orders table"""

    term: str  # e.g. "1 Yr"
    amount_cents: int
    yield_basis_points: Optional[int]
    timestamp: str  # ISO-8601 format, EST timezone

    def to_table_row(self) -> Dict[str, str]:
        return {
            "term": self.term,
            "amount_cents": f"${deci_string(self.amount_cents)}",
            "yield_basis_points": (
                f"{deci_string(self.yield_basis_points)}%"
                if self.yield_basis_points is not None
                else "N/A"
            ),
            "timestamp": self.timestamp,
        }


@dataclass
class YieldCurve:
    """
    - Yield series by term, for one date
    - Used for the graph on the left
    """

    date: str  # formatted "MM/DD/YYYY"
    terms: List[str] = field(default_factory=list)
    yields: List[int] = field(default_factory=list)  # basis points


class HistoricalCurve:
    """
    - Yield timeseries, for one maturity term
    - Used for the graph on the right
    """

    def __init__(self, dates: List[datetime], yields: List[int]):
        self.dates = dates
        self.yields = yields

    def add_data_point(self, date_value: datetime, yield_value: int):
        self.dates.append(date_value)
        self.yields.append(yield_value)

    def to_dict(self):
        return {"dates": self.dates, "yields": self.yields}

    @staticmethod
    def from_dict(d: dict):
        return HistoricalCurve(dates=d["dates"], yields=d["yields"])
