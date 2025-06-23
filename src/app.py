import os
import sys
from dotenv import load_dotenv
from dash import Dash
import dash_bootstrap_components as dbc

# Add the parent directory of src to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print(sys.path)  # Debugging: Print the Python path to verify

from src.components.layout import make_layout  # Ensure correct import path
from src.cache import cache  # Ensure correct import path

# Load environment variables from .env file
load_dotenv()

# Get environment variables
host = os.getenv("HOST", "0.0.0.0")  # Default to 0.0.0.0 if HOST is not set
port = int(os.getenv("PORT", 8050))  # Default to 8050 if PORT is not set

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Quarterback Qualities"

# Initialize cache with the app server
cache.init_app(app.server)

# Set the layout for the app
app.layout = make_layout()

if __name__ == "__main__":
    app.run(host=host, port=port)  # Use host and port from environment variables