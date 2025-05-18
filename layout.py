from dash import Dash, dash_table, dcc
from dash.html import Div, Button, Label, Br
import plotly.graph_objs as go
from datetime import datetime
from typing import NamedTuple, Dict, List
import dataclasses

from db import read_orders
from data_model import Order, YieldCurve, HistoricalCurve
from terms import MATURITY_TERMS, Term
from style import COMMON_STYLE, LABEL_STYLE, SMALL_LABEL_STYLE, BUTTON_STYLE
from prepare_graph_data import prepare_current_yield_curve, prepare_historical_curves


def create_yield_curve_graph(yield_curve: YieldCurve) -> go.Figure:
    percent_yields = [y / 100 for y in yield_curve.yields]
    figure = go.Figure(data=[])
    figure.add_trace(
        go.Scatter(
            x=yield_curve.terms,
            y=percent_yields,
            mode="lines",
            name=yield_curve.date,
            line=dict(color="black"),
        )
    )
    figure.update_layout(
        xaxis_title="Maturity Term",
        yaxis_title="Yield",
        title=f"Treasury Yield Curve {yield_curve.date}",
        yaxis={"ticksuffix": "%"},
    )
    return figure


def create_historical_curve_graph(
    term: Term, historical_curve: HistoricalCurve
) -> go.Figure:
    figure = go.Figure(data=[])
    figure.add_trace(
        go.Scatter(
            x=historical_curve.dates,
            y=[yld / 100 for yld in historical_curve.yields],
            mode="lines",
            name=term,
            line=dict(color="black"),
        )
    )
    figure.update_layout(
        xaxis_title="Time",
        yaxis_title="Yield",
        title=f"Yield for maturity term of <span style='color:red; font-weight:bold'>{term}</span>, historically",
        yaxis={"ticksuffix": "%"},
    )
    return figure


def create_graphs_section(yield_curve: YieldCurve) -> Div:
    """
    - This section is the whole top part of the screen
    - Its structure looks like [graph1, [graph2, slider]]
    """
    return Div(
        [
            Div(
                dcc.Graph(
                    id="graph",
                    figure=create_yield_curve_graph(yield_curve),
                ),
                style={"width": "50%", "padding": "10px"},
            ),
            Div(
                [
                    dcc.Graph(id="historical-curve-graph"),
                    dcc.Slider(
                        min=0,
                        max=len(yield_curve.terms) - 1,
                        step=None,
                        marks={i: term for i, term in enumerate(MATURITY_TERMS)},
                        value=0,
                        id="historical-curve-slider",
                        tooltip={"always_visible": False},
                        updatemode="drag",
                        className="red-slider",
                    ),
                ],
                style={
                    "width": "50%",
                    "padding": "10px",
                    "fontFamily": "Verdana",
                },
            ),
        ],
        style={
            "display": "flex",
            "flexDirection": "row",
            "justifyContent": "space-between",
            "alignItems": "flex-start",
            "width": "100%",
        },
    )


def create_place_order_section(terms: List[Term]) -> Div:
    return Div(
        [
            Div(
                [
                    Label("Term:", style=SMALL_LABEL_STYLE),
                    dcc.Dropdown(terms, "1 Mo", id="term-dropdown", style=COMMON_STYLE),
                ],
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "marginRight": "20px",
                },
            ),
            Div(
                [
                    Label("Amount (Dollars):", style=SMALL_LABEL_STYLE),
                    dcc.Input(
                        id="amount-input",
                        type="number",
                        value=100.00,
                        min=0.01,
                        max=10**6,
                        step=0.01,
                        style=COMMON_STYLE,
                    ),
                ],
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "marginRight": "20px",
                },
            ),
            Div(
                [
                    Label(
                        " ", style=SMALL_LABEL_STYLE
                    ),  # this is just so the alignment is correct
                    Button(
                        "Place order",
                        id="place-order-button",
                        n_clicks=0,
                        style=BUTTON_STYLE,
                    ),
                ],
                style={"display": "flex", "flexDirection": "column"},
            ),
        ],
        style={
            "display": "flex",
            "alignItems": "flex-end",
            "marginBottom": "10px",
        },
    )


def create_orders_table_section() -> dash_table.DataTable:
    return dash_table.DataTable(
        id="table",
        columns=[
            {"name": "Term", "id": "term"},
            {"name": "Amount", "id": "amount_cents"},
            {"name": "Yield", "id": "yield_basis_points"},
            {"name": "Order time", "id": "timestamp"},
        ],
        data=[Order(*db_row).to_table_row() for db_row in read_orders()],
        style_table={"maxWidth": "60vw", "overflowX": "auto"},
        style_cell={
            "textAlign": "left",
            "fontFamily": "Verdana",
            "fontSize": 16,
            "width": "25%",
            "minWidth": "25%",
            "maxWidth": "25%",
        },
        editable=False,
        row_deletable=False,
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
            create_graphs_section(yield_curve),  # both graphs and the slider
            Br(),
            Label("Create order:", style=LABEL_STYLE),
            create_place_order_section(
                yield_curve.terms
            ),  # term dropdown, dollar amount input, button
            Br(),
            Label("Previous orders:", style=LABEL_STYLE),
            create_orders_table_section(),
        ]
    )
