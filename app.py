from dash import Dash, dash_table, dcc, html
from dash.dependencies import Input, Output, State

from datetime import datetime
from collections import defaultdict
import plotly.graph_objs as go

from functools import lru_cache

import sqlite3

from style import COMMON_STYLE, LABEL_STYLE, SMALL_LABEL_STYLE, BUTTON_STYLE
from db import get_orders_from_db, insert_order, DB_NAME
from download import (
    refresh_data_for_new_year,
    get_most_recent_year_with_data_stored,
    refresh_data_for_new_weekday,
    get_stored_data,
)
from build_layout import (
    create_yield_curve_graph,
    create_term_yield_history_graph,
    build_graphs_section,
    build_place_order_section,
    build_orders_table_section,
    make_human_readable,
)


@lru_cache(maxsize=1)
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


@lru_cache(maxsize=1)
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


def get_layout():
    date_value, terms, yields = get_current_yield_curve_data()
    all_data = get_all_data()
    return html.Div(
        [
            dcc.Store(
                id="graph-1-store",
                data={"date_value": date_value, "terms": terms, "yields": yields},
            ),
            dcc.Store(id="graph-2-store", data={"all_data": all_data}),
            build_graphs_section(date_value, terms, yields),
            html.Br(),
            html.Label("Create order:", style=LABEL_STYLE),
            build_place_order_section(terms),
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
    State("graph-1-store", "data"),
    State("graph-2-store", "data"),
)
def update_term_history_graph(slider_index, extra_data1, extra_data2):
    return create_term_yield_history_graph(
        extra_data1["terms"][slider_index], extra_data2["all_data"]
    )


@app.callback(
    Output("table", "data"),
    Input("place-order-button", "n_clicks"),
    State("term-dropdown", "value"),
    State("amount-input", "value"),
    State("table", "data"),
    State("graph-1-store", "data"),
)
def place_order(n_clicks, selected_term, amount, rows, extra_data1):
    terms = extra_data1["terms"]
    yields = extra_data1["yields"]
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

        # global conn doesn't work within dash component thread
        # need to open a new connection within this thread.
        with sqlite3.connect(DB_NAME) as conn:
            insert_order(
                conn,
                new_order["trm"],
                new_order["amt"],
                new_order["yld"],
                new_order["ts"],
            )
    return rows


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8279)
