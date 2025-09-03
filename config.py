import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Backend API Configuration
    BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8080")

    # UI Configuration
    APP_TITLE = "Pitch Perfect - Speech Improvement System"
    APP_DESCRIPTION = "Analyze and improve your speech patterns with AI"

    # Audio Settings
    MAX_AUDIO_DURATION = 300  # 5 minutes in seconds
    MAX_UPLOAD_SIZE = 25      # Maximum file size in MB
    SUPPORTED_FORMATS = ["wav", "mp3", "m4a", "flac"]  # Removed dots

    # API Timeouts
    REQUEST_TIMEOUT = 180

    # Gradio Settings
    SHARE = os.getenv("GRADIO_SHARE", "False").lower() == "true"
    SERVER_NAME = os.getenv("SERVER_NAME", "0.0.0.0")
    SERVER_PORT = int(os.getenv("PORT", os.getenv("SERVER_PORT", "7860")))
