import requests
import json
import os
import mimetypes
import logging
from typing import Optional, Dict, Any
from config import Config

# Configure logger
logger = logging.getLogger(__name__)

class PitchPerfectAPI:
    def __init__(self):
        self.base_url = Config.BACKEND_API_URL.rstrip('/')
        self.timeout = Config.REQUEST_TIMEOUT

    def health_check(self) -> bool:
        """Check if backend API is available"""
        try:
            url = f"{self.base_url}/health"
            logger.info(f"🔍 Checking backend health at: {url}")
            response = requests.get(url, timeout=5)
            logger.info(f"✅ Health check response: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False

    def process_audio(self, audio_file, settings: Optional[Dict] = None) -> Dict[str, Any]:
        """Send audio to backend for processing using /process-audio endpoint"""
        try:
            # Extract settings for individual parameters
            settings = settings or {}
            target_style = settings.get("voice_selection", "professional").lower().replace(" voice", "")
            improvement_focus = settings.get("improvement_focus", ["clarity", "tone"])
            voice_id = settings.get("voice_id")  # Get the actual voice_id
            
            logger.info("="*60)
            logger.info("[FRONTEND->BACKEND] SENDING REQUEST DATA:")
            logger.info(f"  Raw settings received: {settings}")
            logger.info(f"  Extracted voice_id: {voice_id}")
            logger.info(f"  Extracted target_style: {target_style}")
            logger.info(f"  Extracted improvement_focus: {improvement_focus}")
            logger.info("="*60)

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

            # Add voice_id if provided
            if voice_id:
                data["voice_id"] = voice_id

            logger.info(f"[FRONTEND->BACKEND] Final request data: {data}")
            logger.info(f"[FRONTEND->BACKEND] Request URL: {self.base_url}/process-audio")
            logger.info(f"[FRONTEND->BACKEND] Audio filename: {filename}")

            # Use the correct backend endpoint /process-audio
            response = requests.post(
                f"{self.base_url}/process-audio",
                files=files,
                data=data,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()

                logger.info("="*60)
                logger.info("[BACKEND->FRONTEND] RECEIVED RESPONSE DATA:")
                logger.info(f"  Response status code: {response.status_code}")
                logger.info(f"  Response keys: {list(result.keys())}")
                
                # Log each section in detail
                for key, value in result.items():
                    if isinstance(value, dict):
                        logger.info(f"  {key} (dict): {list(value.keys())}")
                        if key == "synthesis" and value:
                            logger.info(f"    synthesis details: voice_used={value.get('voice_used')}, voice_id={value.get('voice_id')}, output_path={value.get('output_path')}")
                        if key == "metadata" and value:
                            logger.info(f"    metadata: voice_id={value.get('voice_id')}, preferences={value.get('preferences')}")
                    elif isinstance(value, list):
                        logger.info(f"  {key} (list): {len(value)} items")
                    else:
                        logger.info(f"  {key}: {type(value).__name__} = {str(value)[:100]}")
                logger.info("="*60)

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
            logger.error("⏱️ Request timeout - audio processing took too long")
            return {"error": "Request timeout - audio processing took too long"}
        except Exception as e:
            logger.error(f"🔌 Connection error: {str(e)}")
            return {"error": f"Connection error: {str(e)}"}

    def get_voice_options(self) -> Dict[str, Any]:
        """Get available TTS voices from backend"""
        try:
            url = f"{self.base_url}/voices"
            logger.info(f"[FRONTEND->BACKEND] Fetching voices from: {url}")
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                voices_data = response.json()
                logger.info("="*60)
                logger.info("[BACKEND->FRONTEND] VOICES RESPONSE:")
                logger.info(f"  Status: {response.status_code}")
                logger.info(f"  Number of voices: {len(voices_data.get('voices', []))}")
                
                for i, voice in enumerate(voices_data.get('voices', [])[:3]):  # Log first 3
                    logger.info(f"  Voice {i+1}: {voice['name']} (ID: {voice['voice_id']}, Category: {voice['category']})")
                    if voice.get('description'):
                        logger.info(f"    Description: {voice['description'][:80]}...")
                logger.info("="*60)
                return voices_data
            else:
                logger.warning(f"⚠️ Failed to fetch voices: HTTP {response.status_code}")
                # Fallback to hardcoded options
                return self._get_fallback_voices()

        except Exception as e:
            logger.error(f"❌ Error fetching voices: {e}")
            return self._get_fallback_voices()

    def _get_fallback_voices(self) -> Dict[str, Any]:
        """Fallback voice options when backend is unavailable"""
        return {
            "voices": [
                {"voice_id": None, "name": "Default Voice", "category": "Standard", "description": "Default system voice"},
                {"voice_id": "onwK4e9ZLuTAKqWW03F9", "name": "Professional Voice", "category": "Professional", "description": "Clear professional voice"},
                {"voice_id": None, "name": "Casual Voice", "category": "Casual", "description": "Friendly casual voice"}
            ]
        }
