from dash import Dash, dash_table, dcc, html
from dash.dependencies import Input, Output, State

from datetime import datetime
import plotly.graph_objs as go

import sqlite3

from style import COMMON_STYLE, LABEL_STYLE, BUTTON_STYLE
from db import get_orders_from_db, insert_order
from download import (
    refresh_data_for_new_year,
    get_most_recent_year_with_data_stored,
    refresh_data_for_new_weekday,
    get_data,
)


def format_timestamp(ts_str):
    try:
        return datetime.strptime(ts_str, "%Y%m%d%H%M").strftime("%Y-%m-%d %H:%M")
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


refresh_data_for_new_year()

most_recent_year_with_data = get_most_recent_year_with_data_stored()
# will usually be the current year, but could be the previous year e.g. if it's Saturday Jan 1

refresh_data_for_new_weekday(most_recent_year_with_data)
data = get_data(most_recent_year_with_data)

first_line, second_line = data[:2]
terms = [col.replace("onth", "o") for col in first_line[1:]]
date_value, yields = second_line[0], [float(val) for val in second_line[1:]]


def create_graph():
    fig = go.Figure(data=[])
    fig.add_trace(
        go.Scatter(
            x=terms,
            y=yields,
            mode="lines",
            name=date_value,
            line=dict(color="blue"),
        )
    )
    # fig.add_trace(
    #     go.Scatter(
    #         x=cols,
    #         y=yield_vals2,
    #         mode="lines",
    #         name=date_val2,
    #         line=dict(color="red"),
    #     )
    # )
    fig.update_layout(
        xaxis_title="Maturity Term",
        yaxis_title="Yield",
        title="Treasury Yield Curve",
        yaxis={"ticksuffix": "%"},
        showlegend=True,
    )
    # fig.data = [fig.data[0]]
    # fig.show()
    return fig








def get_layout():
    return html.Div(
        [
            html.Div(
                dcc.Graph(id="graph", figure=create_graph()), style={"maxWidth": "50vw"}
            ),
            html.Br(),
            html.Label("Create order:", style=LABEL_STYLE),
            html.Div(
                [
                    dcc.Dropdown(terms, "1 Mo", id="term-dropdown", style=COMMON_STYLE),
                    dcc.Input(
                        id="amount-input",
                        type="number",
                        value=100.00,
                        min=0,
                        max=10**6,
                        step=0.01,
                        style=COMMON_STYLE,
                    ),
                    html.Button(
                        "Place order",
                        id="place-order-button",
                        n_clicks=0,
                        style=BUTTON_STYLE,
                    ),
                ],
                style={"display": "flex", "alignItems": "center"},
            ),
            html.Br(),
            html.Label("Previous orders:", style=LABEL_STYLE),
            dash_table.DataTable(
                id="table",
                columns=[
                    {"name": "Term", "id": "trm"},
                    {"name": "Amount", "id": "amt"},
                    {"name": "Yield", "id": "yld"},
                    {"name": "Order time", "id": "ts"},
                ],
                data=table_format(
                    get_orders_from_db()
                ),  # executes on both load and refresh
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
            ),
        ]
    )

app = Dash(__name__)
app.layout = get_layout


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
            "ts": datetime.now().strftime("%Y%m%d%H%M"),
        }
        rows.insert(0, make_human_readable(new_order))

        # global conn wouldn't work
        # need to open a new connection within this thread.
        conn = sqlite3.connect("treasury_rates.db")
        insert_order(
            conn, new_order["trm"], new_order["amt"], new_order["yld"], new_order["ts"]
        )
        conn.close()
    return rows


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8279)
