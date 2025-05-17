from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, List


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
    date: str  # e.g. 05/14/2021
    terms: List[str] = field(default_factory=list)
    yields: List[int] = field(default_factory=list)  # basis points


class YieldHistory:
    def __init__(self, dates: List[str], yields: List[int]):
        self.dates = dates
        self.yields = yields

    def add_data_point(self, date_value: str, yield_value: int):
        self.dates.append(date_value)
        self.yields.append(yield_value)

    def to_dict(self):
        return {"dates": self.dates, "yields": self.yields}

    @staticmethod
    def from_dict(d: dict):
        return YieldHistory(dates=d["dates"], yields=d["yields"])


def deci_string(n: int) -> str:
    """
    357 -> "3.57"
    4562 -> "45.62"
    89 -> "0.89"
    100 -> 1.00
    """
    return f"{n // 100}.{str(n % 100).zfill(2)}"


def get_terms(csv_first_row: List[str]):
    pass
