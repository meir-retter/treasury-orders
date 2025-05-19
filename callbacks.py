from dash.dependencies import Input, Output, State
from datetime import datetime
import sqlite3
from typing import Dict, List, Any

from data_model import Order, YieldCurve, HistoricalCurve
from db import insert_order, DB_NAME
from terms import MATURITY_TERMS, Term
from layout import create_historical_curve_graph


def create_new_order(
    yield_curve: Dict[str, Any], selected_term: Term, amount_dollars: float
) -> Order:
    index: int = yield_curve["terms"].index(selected_term)
    yield_for_selected_term: int = yield_curve["yields"][index]

    order = Order(
        term=selected_term,
        amount_cents=int(round(amount_dollars * 100)),
        yield_basis_points=yield_for_selected_term,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    return order


def register_callbacks(app):
    @app.callback(
        Output("historical-curve-graph", "figure"),
        Input("historical-curve-slider", "value"),
        State("historical-curves", "data"),
    )
    def update_historical_curve_graph(
        slider_index: int, historical_curves: Dict[str, Dict[str, List[Any]]]
    ):
        term = MATURITY_TERMS[slider_index]
        return create_historical_curve_graph(
            term, HistoricalCurve.from_dict(historical_curves[term])
        )

    @app.callback(
        Output("table", "data"),
        Input("place-order-button", "n_clicks"),
        State("term-dropdown", "value"),
        State("amount-input", "value"),
        State("table", "data"),
        State("yield-curve", "data"),
    )
    def place_order(
        n_clicks: int,
        selected_term: Term,
        amount_dollars: float,
        table_rows: List[Dict[str, Any]],
        yield_curve: Dict[str, Any],
    ):
        # amount_dollars may actually be stored as int or float
        # this is because Dash will use int if the order is placed with e.g. 55 as the amount
        # but, it will use a float if it's placed with 55.01
        # in any case, we are going to immediately multiply by 100, round, and cast to int for the number of cents
        if n_clicks > 0 and selected_term in yield_curve["terms"]:
            order: Order = create_new_order(yield_curve, selected_term, amount_dollars)
            table_rows.insert(0, order.to_table_row())

            # global conn doesn't work within dash component thread
            # need to open a new connection within this thread.
            with sqlite3.connect(DB_NAME) as conn:
                insert_order(conn, order)
        return table_rows
