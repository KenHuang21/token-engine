import os
import sys

# Add the project root to sys.path so we can import backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app

# Vercel expects a variable named 'app' or handler
# We already imported 'app'
