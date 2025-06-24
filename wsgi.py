import os
import sys

# Add your project directory to Python path
path = '/home/Jacobdking1999/qb-qualities'
if path not in sys.path:
    sys.path.append(path)

# Import your Dash application
from src.app import app

# Get the Flask app
application = app.server
