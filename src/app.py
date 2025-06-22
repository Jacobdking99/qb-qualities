from dash import Dash, dcc
from components.layout import make_layout
import dash_bootstrap_components as dbc
from cache import cache  # Import the centralized cache

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Quarterback Qualities"

# Initialize cache with the app server
cache.init_app(app.server)

# Wrap layout in a loading spinner
app.layout = make_layout()  # Remove global loading spinner for deployment

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)  # Use host and port suitable for Render