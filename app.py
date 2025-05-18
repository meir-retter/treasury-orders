from dash import Dash, dash_table, dcc, html
from dash.dependencies import Input, Output, State

import dataclasses

from datetime import datetime
from collections import defaultdict
import plotly.graph_objs as go

from functools import lru_cache
from typing import Tuple, List, Dict, Any

import sqlite3

from style import COMMON_STYLE, LABEL_STYLE, SMALL_LABEL_STYLE, BUTTON_STYLE
from db import insert_order, DB_NAME
from download import get_yield_curve_data_for_this_year, read_downloaded_csv
from build_layout import (
    create_yield_curve_graph,
    create_term_history_graph,
    build_graphs_section,
    build_place_order_section,
    build_orders_table_section,
)

from utils import Order, YieldCurve, TermHistory, deci_string
from constants import MATURITY_TERMS
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@lru_cache(maxsize=1)
def get_current_yield_curve() -> YieldCurve:
    data = get_yield_curve_data_for_this_year()
    first_line, second_line = data[:2]
    terms = [col.replace("onth", "o") for col in first_line[1:]]
    date_value, yields = second_line[0], [
        int(val.replace(".", "")) for val in second_line[1:]
    ]
    return YieldCurve(date_value, terms, yields)


@lru_cache(maxsize=1)
def get_term_histories() -> Dict[str, TermHistory]:
    term_histories = defaultdict(lambda: TermHistory([], []))
    for year in range(1990, 2026):
        csv_rows = read_downloaded_csv(year)
        terms = [term.replace("onth", "o") for term in csv_rows[0][1:]]
        for row in reversed(csv_rows[1:]):
            row_date = row[0]
            yield_values = [(int(x.replace(".", "")) if x else None) for x in row[1:]]
            for term, yield_value in zip(terms, yield_values):
                if yield_value is not None:
                    term_histories[term].add_data_point(
                        datetime.strptime(row_date, "%m/%d/%Y"), yield_value
                    )
    return term_histories


def get_layout():
    yield_curve = get_current_yield_curve()
    term_histories = get_term_histories()
    return html.Div(
        [
            dcc.Store(
                id="yield-curve",
                data=dataclasses.asdict(yield_curve),
            ),
            dcc.Store(
                id="term-histories",
                data={k: v.to_dict() for k, v in term_histories.items()},
            ),
            build_graphs_section(yield_curve),
            html.Br(),
            html.Label("Create order:", style=LABEL_STYLE),
            build_place_order_section(yield_curve.terms),
            html.Br(),
            html.Label("Previous orders:", style=LABEL_STYLE),
            build_orders_table_section(),
        ]
    )


app = Dash(__name__)
app.layout = get_layout


@app.callback(
    Output("term-yield-history-graph", "figure"),
    Input("term-yield-history-slider", "value"),
    State("term-histories", "data"),
)
def update_term_history_graph(slider_index: int, term_histories):
    term = MATURITY_TERMS[slider_index]
    return create_term_history_graph(term, TermHistory.from_dict(term_histories[term]))


@app.callback(
    Output("table", "data"),
    Input("place-order-button", "n_clicks"),
    State("term-dropdown", "value"),
    State("amount-input", "value"),
    State("table", "data"),
    State("yield-curve", "data"),
)
def place_order(n_clicks, selected_term, amount_dollars, rows, yield_curve):
    terms = yield_curve["terms"]
    yields = yield_curve["yields"]
    if n_clicks > 0 and selected_term in terms:
        try:
            idx = terms.index(selected_term)
            yld = yields[idx]
        except (ValueError, IndexError):
            yld = None
        new_order = Order(
            selected_term,
            int(amount_dollars * 100),
            yld,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        rows.insert(0, new_order.to_table_row())

        # global conn doesn't work within dash component thread
        # need to open a new connection within this thread.
        with sqlite3.connect(DB_NAME) as conn:
            insert_order(conn, new_order)
    return rows


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8279)
