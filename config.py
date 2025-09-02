import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Environment detection
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

    # Backend API Configuration
    BACKEND_API_URL = os.getenv("BACKEND_API_URL", "https://pitch-perfect-backend-792590041292.europe-west1.run.app/")

    # Google Cloud Storage Configuration
    GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "pp-pitchperfect-lewagon-raw-data")
    GCS_MODEL_PATH = os.getenv("GCS_MODEL_PATH", "models/")

    # Google Cloud Project
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "pitchperfect-lewagon")

    # UI Configuration
    APP_TITLE = "Pitch Perfect - Speech Improvement System"
    APP_DESCRIPTION = "Analyze and improve your speech patterns with AI"

    # Audio Settings
    MAX_AUDIO_DURATION = 300  # 5 minutes
    SUPPORTED_FORMATS = [".wav", ".mp3", ".m4a", ".flac"]

    # API Timeouts
    REQUEST_TIMEOUT = 120  # Increased for production

    # Gradio Settings
    if ENVIRONMENT == "production":
        SHARE = False  # Don't use gradio.live in production
        SERVER_NAME = "0.0.0.0"
        SERVER_PORT = int(os.getenv("PORT", "8080"))  # Cloud Run uses PORT env var
    else:
        SHARE = os.getenv("GRADIO_SHARE", "True").lower() == "true"
        SERVER_NAME = os.getenv("SERVER_NAME", "0.0.0.0")
        SERVER_PORT = int(os.getenv("SERVER_PORT", "7860"))

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Authentication (if needed)
    AUTH_ENABLED = os.getenv("AUTH_ENABLED", "false").lower() == "true"
