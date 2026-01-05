"""
Vercel Serverless Function Entry Point
This file is required by Vercel to deploy the Flask app as a serverless function.
"""

import sys
import os

# Add the project root to the path for proper imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

# Create the Flask app instance for Vercel
app = create_app()

# Vercel requires the app to be named 'app' or 'handler'
# The app instance is exposed for the Vercel Python runtime
