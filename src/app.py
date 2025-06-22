from dash import Dash, dcc
from components.layout import make_layout
import dash_bootstrap_components as dbc
from cache import cache  # Import the centralized cache

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Quarterback Qualities"

# Initialize cache with the app server
cache.init_app(app.server)

# Wrap layout in a loading spinner
app.layout = dcc.Loading(children=make_layout(), type="circle")

if __name__ == "__main__":
    app.run(debug=True)