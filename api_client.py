import requests
import json
import os
import mimetypes
from typing import Optional, Dict, Any
from config import Config

class PitchPerfectAPI:
    def __init__(self):
        self.base_url = Config.BACKEND_API_URL.rstrip('/')
        self.timeout = Config.REQUEST_TIMEOUT

    def health_check(self) -> bool:
        """Check if backend API is available"""
        try:
            url = f"{self.base_url}/health"
            print(f"Checking backend health at: {url}")
            response = requests.get(url, timeout=5)
            print(f"Health check response: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False

    def process_audio(self, audio_file, settings: Optional[Dict] = None) -> Dict[str, Any]:
        """Send audio to backend for processing using /process-audio endpoint"""
        try:
            # Extract settings for individual parameters
            settings = settings or {}
            target_style = settings.get("voice_selection", "professional").lower().replace(" voice", "")
            improvement_focus = settings.get("improvement_focus", ["clarity", "tone"])

            # Convert improvement_focus list to string if needed
            if isinstance(improvement_focus, list):
                improvement_focus = ",".join(improvement_focus).lower()

            # Determine MIME type from file extension if not available
            import mimetypes
            audio_file.seek(0)  # Reset file pointer

            # Get filename from the file path if it's a string path
            if hasattr(audio_file, 'name'):
                filename = os.path.basename(audio_file.name)
            else:
                filename = "audio.wav"  # Default fallback

            # Guess MIME type from filename
            mime_type, _ = mimetypes.guess_type(filename)
            if not mime_type or not mime_type.startswith('audio/'):
                # Default to wav if we can't determine
                mime_type = 'audio/wav'

            # Prepare files with proper MIME type
            files = {"audio_file": (filename, audio_file, mime_type)}
            data = {
                "target_style": target_style,
                "improvement_focus": improvement_focus,
                "save_audio": True
            }

            # Use the correct backend endpoint /process-audio
            response = requests.post(
                f"{self.base_url}/process-audio",
                files=files,
                data=data,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()

                # Debug: Print the actual response structure (optional, can be removed in production)
                print("=== BACKEND RESPONSE DEBUG ===")
                print("Keys in response:", list(result.keys()))
                for key, value in result.items():
                    if isinstance(value, dict):
                        print(f"{key}: {list(value.keys())}")
                    else:
                        print(f"{key}: {type(value)}")
                print("=== END DEBUG ===")

                # Return the complete backend response with all fields intact
                # The backend already provides well-structured data
                formatted_result = {
                    # Basic info
                    "timestamp": result.get("timestamp"),
                    "session_id": result.get("session_id"),
                    "processing_status": result.get("processing_status", "completed"),
                    "input_audio": result.get("input_audio"),
                    
                    # Transcription data
                    "transcription": result.get("transcription", {}),
                    
                    # Analysis results
                    "sentiment": result.get("sentiment", {}),
                    "tonal": result.get("tonal", {}),
                    
                    # Improvements
                    "improvements": result.get("improvements", {}),
                    
                    # Audio synthesis
                    "synthesis": result.get("synthesis", {}),
                    
                    # Processing metrics
                    "metrics": result.get("metrics", {}),
                }

                # Add improved audio path for easy access
                if result.get("synthesis", {}).get("output_path"):
                    formatted_result["improved_audio_path"] = result["synthesis"]["output_path"]

                return formatted_result
            else:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", f"HTTP {response.status_code}")
                except:
                    error_detail = f"HTTP {response.status_code}"

                return {"error": f"API Error: {error_detail}"}

        except requests.exceptions.Timeout:
            return {"error": "Request timeout - audio processing took too long"}
        except Exception as e:
            return {"error": f"Connection error: {str(e)}"}

    def get_voice_options(self) -> Dict[str, Any]:
        """Get available TTS voices - use fallback since backend doesn't have /voices endpoint"""
        # Since your backend doesn't have a /voices endpoint, provide hardcoded options
        # that match your ElevenLabs/TTS configuration
        return {
            "voices": [
                "Professional Voice",
                "Casual Voice",
                "Academic Voice",
                "Motivational Voice",
                "Default Voice"
            ]
        }
