from dash import Dash, dash_table, dcc, html
from dash.dependencies import Input, Output, State

from datetime import datetime
from collections import defaultdict
import plotly.graph_objs as go

import sqlite3

from style import COMMON_STYLE, LABEL_STYLE, SMALL_LABEL_STYLE, BUTTON_STYLE
from db import get_orders_from_db, insert_order, DB_NAME
from download import (
    refresh_data_for_new_year,
    get_most_recent_year_with_data_stored,
    refresh_data_for_new_weekday,
    get_stored_data,
)


def format_timestamp(ts_str):
    try:
        return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ts_str


def make_human_readable(order):
    return {
        "trm": order["trm"],
        "amt": f"${order['amt']:,.2f}" if order["amt"] is not None else "N/A",
        "yld": f"{round(order['yld'], 2)}%" if order["yld"] is not None else "N/A",
        "ts": format_timestamp(order["ts"]),
    }


def table_format(rows):
    return [
        make_human_readable({"trm": row[0], "amt": row[1], "yld": row[2], "ts": row[3]})
        for row in rows
    ]


def get_current_yield_curve_data():
    refresh_data_for_new_year()

    most_recent_year_with_data = get_most_recent_year_with_data_stored()
    # will usually be the current year, but could be the previous year e.g. if it's Saturday Jan 1

    refresh_data_for_new_weekday(most_recent_year_with_data)
    data = get_stored_data(most_recent_year_with_data)

    first_line, second_line = data[:2]
    terms = [col.replace("onth", "o") for col in first_line[1:]]
    date_value, yields = second_line[0], [float(val) for val in second_line[1:]]
    return date_value, terms, yields


# from download import download_csv_and_write_to_file
# for y in range(1990, 2025):
#     download_csv_and_write_to_file(y)
#     print(y, "done")


def get_all_data():
    all_data = defaultdict(lambda: {"dates": [], "yields": []})
    for year in range(1990, 2026):
        year_data = get_stored_data(year)
        cols = [col.replace("onth", "o") for col in year_data[0]]
        for i in reversed(range(1, len(year_data))):
            row = year_data[i]
            row_date = row[0]
            for j in range(1, len(row)):
                term = cols[j]
                yield_value = float(row[j]) if row[j] else None
                if yield_value is not None:
                    all_data[term]["dates"].append(
                        datetime.strptime(row_date, "%m/%d/%Y")
                    )
                    all_data[term]["yields"].append(yield_value)
    return all_data


date_value, terms, yields = get_current_yield_curve_data()
all_data = get_all_data()


def create_yield_curve_graph():
    fig = go.Figure(data=[])
    fig.add_trace(
        go.Scatter(
            x=terms,
            y=yields,
            mode="lines",
            name=date_value,
            line=dict(color="black"),
        )
    )
    fig.update_layout(
        xaxis_title="Maturity Term",
        yaxis_title="Yield",
        title=f"Treasury Yield Curve {date_value}",
        yaxis={"ticksuffix": "%"},
    )
    return fig


def create_term_yield_history_graph(term):
    fig = go.Figure(data=[])
    fig.add_trace(
        go.Scatter(
            x=all_data[term]["dates"],
            y=all_data[term]["yields"],
            mode="lines",
            name=term,
            line=dict(color="black"),
        )
    )
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Yield",
        title=f"Yield for maturity term of <span style='color:red; font-weight:bold'>{term}</span>, historically",
        yaxis={"ticksuffix": "%"},
    )
    return fig


def build_graphs_section():
    return html.Div(
        [
            html.Div(
                dcc.Graph(id="graph", figure=create_yield_curve_graph()),
                style={"width": "50%", "padding": "10px"},
            ),
            html.Div(
                [
                    dcc.Graph(id="term-yield-history-graph"),
                    dcc.Slider(
                        min=0,
                        max=len(terms) - 1,
                        step=None,
                        marks={i: term for i, term in enumerate(terms)},
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

def build_place_order_section():
    return html.Div(
        [
            html.Div(
                [
                    html.Label("Term:", style=SMALL_LABEL_STYLE),
                    dcc.Dropdown(
                        terms, "1 Mo", id="term-dropdown", style=COMMON_STYLE
                    ),
                ],
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "marginRight": "20px",
                },
            ),
            html.Div(
                [
                    html.Label("Amount (Dollars):", style=SMALL_LABEL_STYLE),
                    dcc.Input(
                        id="amount-input",
                        type="number",
                        value=100.00,
                        min=0,
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
            html.Div(
                [
                    html.Label(
                        " ", style=SMALL_LABEL_STYLE
                    ),  # this is just so the alignment is correct
                    html.Button(
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
        }
    )


def build_orders_table_section():
    return dash_table.DataTable(
        id="table",
        columns=[
            {"name": "Term", "id": "trm"},
            {"name": "Amount", "id": "amt"},
            {"name": "Yield", "id": "yld"},
            {"name": "Order time", "id": "ts"},
        ],
        data=table_format(
            get_orders_from_db()
        ),
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


def get_layout():
    return html.Div(
        [
            build_graphs_section(),
            html.Br(),
            html.Label("Create order:", style=LABEL_STYLE),
            build_place_order_section(),
            html.Br(),
            html.Label("Previous orders:", style=LABEL_STYLE),
            build_orders_table_section()
        ]
    )


app = Dash(__name__)
app.layout = get_layout


@app.callback(
    Output("term-yield-history-graph", "figure"),
    Input("term-yield-history-slider", "value"),
)
def update_term_history_graph(slider_index):
    return create_term_yield_history_graph(terms[slider_index])


@app.callback(
    Output("table", "data"),
    Input("place-order-button", "n_clicks"),
    State("term-dropdown", "value"),
    State("amount-input", "value"),
    State("table", "data"),
)
def place_order(n_clicks, selected_term, amount, rows):
    if n_clicks > 0 and selected_term in terms:
        try:
            idx = terms.index(selected_term)
            yld = yields[idx]
        except (ValueError, IndexError):
            yld = None

        new_order = {
            "trm": selected_term,
            "amt": amount,
            "yld": round(yld, 2) if yld is not None else "N/A",
            "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        rows.insert(0, make_human_readable(new_order))

        # global conn doesnt work within dash component thread
        # need to open a new connection within this thread.
        with sqlite3.connect(DB_NAME) as conn:
            insert_order(
                conn, new_order["trm"], new_order["amt"], new_order["yld"], new_order["ts"]
            )
    return rows


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8279)
