import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/torq-app'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variables
os.environ['GROQ_API_KEY'] = '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'

# Import Flask app
from app import app as application
