import os
from dotenv import load_dotenv
from dash import Dash, dcc
from components.layout import make_layout
import dash_bootstrap_components as dbc
from cache import cache  # Import the centralized cache

# Load environment variables from .env file
load_dotenv()

# Get environment variables
host = os.getenv("HOST", "0.0.0.0")  # Default to 0.0.0.0 if HOST is not set
port = int(os.getenv("PORT", 8080))  # Default to 8080 if PORT is not set

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Quarterback Qualities"

# Initialize cache with the app server
cache.init_app(app.server)

# Wrap layout in a loading spinner
app.layout = make_layout()  # Remove global loading spinner for deployment

if __name__ == "__main__":
    app.run(host=host, port=port)  # Use host and port from environment variables