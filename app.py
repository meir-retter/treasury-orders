from dash import Dash

from layout import create_app_layout
from callbacks import register_callbacks
from db import init_db

init_db()

app = Dash(__name__)
app.layout = create_app_layout

register_callbacks(app)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8279)
