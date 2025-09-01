import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Backend API Configuration
    BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

    # UI Configuration
    APP_TITLE = "Pitch Perfect - Speech Improvement System"
    APP_DESCRIPTION = "Analyze and improve your speech patterns with AI"

    # Audio Settings
    MAX_AUDIO_DURATION = 300  # 5 minutes
    SUPPORTED_FORMATS = [".wav", ".mp3", ".m4a", ".flac"]

    # API Timeouts
    REQUEST_TIMEOUT = 60

    # Gradio Settings
    SHARE = os.getenv("GRADIO_SHARE", "False").lower() == "true"
    SERVER_NAME = os.getenv("SERVER_NAME", "0.0.0.0")
    SERVER_PORT = int(os.getenv("SERVER_PORT", "7860"))
