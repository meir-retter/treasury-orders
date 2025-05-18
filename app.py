from dash import Dash, dash_table, dcc, html
from dash.html import Div, Label, Br
from dash.dependencies import Input, Output, State

import plotly.graph_objs as go

import dataclasses
from datetime import datetime
import sqlite3

from style import COMMON_STYLE, LABEL_STYLE, SMALL_LABEL_STYLE, BUTTON_STYLE
from db import insert_order, DB_NAME
from data_model import Order, HistoricalCurve
from terms import MATURITY_TERMS
from prepare_graph_data import prepare_current_yield_curve, prepare_historical_curves
from layout import (
    create_yield_curve_graph,
    create_historical_curve_graph,
    create_graphs_section,
    create_place_order_section,
    create_orders_table_section,
)


def create_app_layout() -> Div:
    yield_curve = prepare_current_yield_curve()
    historical_curves = prepare_historical_curves()

    return Div(
        [
            dcc.Store(
                id="yield-curve",
                data=dataclasses.asdict(yield_curve),
            ),
            dcc.Store(
                id="historical-curves",
                data={
                    term: historical_curve.to_dict()
                    for term, historical_curve in historical_curves.items()
                },
            ),
            create_graphs_section(yield_curve),
            Br(),
            Label("Create order:", style=LABEL_STYLE),
            create_place_order_section(yield_curve.terms),
            Br(),
            Label("Previous orders:", style=LABEL_STYLE),
            create_orders_table_section(),
        ]
    )


app = Dash(__name__)
app.layout = create_app_layout


@app.callback(
    Output("historical-curve-graph", "figure"),
    Input("historical-curve-slider", "value"),
    State("historical-curves", "data"),
)
def update_historical_curve_graph(slider_index: int, historical_curves):
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
def place_order(n_clicks, selected_term, amount_dollars, rows, yield_curve):
    if n_clicks > 0 and selected_term in yield_curve["terms"]:
        index: int = yield_curve["terms"].index(selected_term)
        yield_for_selected_term: int = yield_curve["yields"][index]

        order = Order(
            term=selected_term,
            amount_cents=int(amount_dollars * 100),
            yield_basis_points=yield_for_selected_term,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        rows.insert(0, order.to_table_row())

        # global conn doesn't work within dash component thread
        # need to open a new connection within this thread.
        with sqlite3.connect(DB_NAME) as conn:
            insert_order(conn, order)
    return rows


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8279)
