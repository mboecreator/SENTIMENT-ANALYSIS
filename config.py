import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables
load_dotenv()

# Model configuration
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment"
MAX_LENGTH = 512

# Application configuration
DEBUG = True
PORT = 5000
HOST = '0.0.0.0'

# File paths
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Security configuration
SECRET_KEY = os.urandom(24)
PERMANENT_SESSION_LIFETIME = timedelta(days=7)

# Analysis settings
MAX_TEXT_LENGTH = 1000  # Maximum length of text for analysis
MAX_BATCH_SIZE = 100   # Maximum number of texts in batch analysis 