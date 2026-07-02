import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production')
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024