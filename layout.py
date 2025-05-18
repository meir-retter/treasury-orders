from dash import Dash, dash_table, dcc
from dash.html import Div, Button, Label
import plotly.graph_objs as go
from style import COMMON_STYLE, LABEL_STYLE, SMALL_LABEL_STYLE, BUTTON_STYLE

from datetime import datetime
from typing import NamedTuple, Dict, List

from db import read_orders
from data_model import Order, YieldCurve, History

from terms import MATURITY_TERMS, Term


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


def create_history_graph(term: Term, history: History) -> go.Figure:
    figure = go.Figure(data=[])
    figure.add_trace(
        go.Scatter(
            x=history.dates,
            y=[yld / 100 for yld in history.yields],
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
                    dcc.Graph(id="term-yield-history-graph"),
                    dcc.Slider(
                        min=0,
                        max=len(yield_curve.terms) - 1,
                        step=None,
                        marks={i: term for i, term in enumerate(MATURITY_TERMS)},
                        value=0,
                        id="term-yield-history-slider",
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


def create_orders_table_section():
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
