import requests
import json
from typing import Optional, Dict, Any
from config import Config

class PitchPerfectAPI:
    def __init__(self):
        self.base_url = Config.BACKEND_API_URL
        self.timeout = Config.REQUEST_TIMEOUT

    def health_check(self) -> bool:
        """Check if backend API is available"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

    def process_audio(self, audio_file, settings: Optional[Dict] = None) -> Dict[str, Any]:
        """Send audio to backend for processing"""
        try:
            files = {"audio": audio_file}
            data = {"settings": json.dumps(settings or {})}

            response = requests.post(
                f"{self.base_url}/process",
                files=files,
                data=data,
                timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API Error: {response.status_code}"}

        except requests.exceptions.Timeout:
            return {"error": "Request timeout - audio processing took too long"}
        except Exception as e:
            return {"error": f"Connection error: {str(e)}"}

    def get_voice_options(self) -> Dict[str, Any]:
        """Get available TTS voices from backend"""
        try:
            response = requests.get(f"{self.base_url}/voices", timeout=10)
            if response.status_code == 200:
                return response.json()
            return {"voices": []}
        except:
            return {"voices": []}
