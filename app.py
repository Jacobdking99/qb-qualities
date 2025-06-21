from dash import Dash, html, dcc
from home import make_home_layout
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Quarterback Qualities"
app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                make_home_layout(),
                className="mb-4"
            )
        )
    ],
    fluid=True,
    className="p-4"
)
if __name__ == "__main__":
    app.run(debug=True)