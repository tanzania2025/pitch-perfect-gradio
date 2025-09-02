import gradio as gr
import os
import logging
from google.cloud import storage
from api_client import PitchPerfectAPI
from config import Config
from components.audio_input import create_audio_input

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Initialize API client
api_client = PitchPerfectAPI()

class GCSModelLoader:
    """Load models from Google Cloud Storage"""

    def __init__(self):
        self.client = storage.Client(project=Config.GCP_PROJECT_ID)
        self.bucket = self.client.bucket(Config.GCS_BUCKET_NAME)

    def get_available_models(self):
        """Get list of available models from GCS"""
        try:
            blobs = self.bucket.list_blobs(prefix=Config.GCS_MODEL_PATH)
            models = [blob.name.split('/')[-1] for blob in blobs if blob.name.endswith('.pth')]
            logger.info(f"Found {len(models)} models in GCS")
            return models
        except Exception as e:
            logger.error(f"Failed to list models from GCS: {e}")
            return []

try:
    model_loader = GCSModelLoader()
except Exception as e:
    logger.warning(f"Skipping GCS model loader initialization: {e}")
    model_loader = None

# Initialize API client
api_client = PitchPerfectAPI()

def process_speech(audio_file, voice_selection, analysis_depth, improvement_focus, progress=gr.Progress()):
    if audio_file is None:
        return None, "Please upload an audio file", None, None, None

    if not api_client.health_check():
        return None, "❌ Backend service is unavailable", None, None, None

    settings = {
        "voice_selection": voice_selection,
        "analysis_depth": analysis_depth,
        "improvement_focus": improvement_focus
    }

    progress(0.1, desc="Uploading audio...")

    with open(audio_file, "rb") as f:
        progress(0.3, desc="Processing speech...")
        result = api_client.process_audio(f, settings)

    if "error" in result:
        return None, f"❌ {result['error']}", None, None, None

    progress(0.9, desc="Finalizing results...")

    transcript = result.get("transcript", "")
    sentiment_analysis = result.get("sentiment_analysis", {})
    tonal_analysis = result.get("tonal_analysis", {})
    improvements = result.get("improvements", "")
    improved_audio = result.get("improved_audio_path")

    analysis_text = format_analysis_results(sentiment_analysis, tonal_analysis)

    return improved_audio, transcript, analysis_text, improvements, "✅ Processing complete!"


def format_analysis_results(sentiment, tonal):
    """Format analysis results for display"""
    results = []

    if sentiment:
        results.append(f"**Sentiment Analysis:**")
        results.append(f"- Overall Sentiment: {sentiment.get('label', 'N/A')}")
        results.append(f"- Confidence: {sentiment.get('score', 0):.2%}")

    if tonal:
        results.append(f"\n**Tonal Analysis:**")
        results.append(f"- Pitch Variation: {tonal.get('pitch_variation', 'N/A')}")
        results.append(f"- Speech Rate: {tonal.get('speech_rate', 'N/A')}")
        results.append(f"- Energy Level: {tonal.get('energy_level', 'N/A')}")

    return "\n".join(results)

def create_interface():
    """Create the main Gradio interface"""

    try:
        voice_data = api_client.get_voice_options() or {}
        voice_choices = voice_data.get("voices")
        if not voice_choices:
            logger.warning("No voices returned by backend, falling back to Default Voice")
            voice_choices = ["Default Voice"]
    except Exception as e:
        logger.error(f"Error fetching voice options: {e}")
        voice_choices = ["Default Voice"]


    voice_selection = gr.Dropdown(
    choices=voice_choices,
    value=voice_choices[0],   # always safe now
    label="TTS Voice"
    )


    with gr.Blocks(
        title=Config.APP_TITLE,
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        .audio-player {
            margin: 10px 0;
        }
        """
    ) as demo:

        gr.Markdown(f"# {Config.APP_TITLE}")
        gr.Markdown(Config.APP_DESCRIPTION)

        with gr.Row():
            with gr.Column(scale=1):
                # Input Section
                gr.Markdown("## 🎤 Upload Your Speech")
                audio_input = gr.Audio(
                    label="Record or Upload Audio",
                    type="filepath",
                    format="wav"
                )

                # Settings Panel
                gr.Markdown("## ⚙️ Settings")
                voice_selection = gr.Dropdown(
                    choices=voice_choices,
                    value=voice_choices[0] if voice_choices else "Default Voice",
                    label="TTS Voice"
                )

                analysis_depth = gr.Radio(
                    choices=["Basic", "Detailed", "Comprehensive"],
                    value="Detailed",
                    label="Analysis Depth"
                )

                improvement_focus = gr.CheckboxGroup(
                    choices=["Clarity", "Tone", "Pace", "Confidence", "Emotion"],
                    value=["Clarity", "Tone"],
                    label="Improvement Focus"
                )

                process_btn = gr.Button("🚀 Analyze Speech", variant="primary", size="lg")

            with gr.Column(scale=2):
                # Results Section
                gr.Markdown("## 📊 Results")

                status = gr.Textbox(label="Status", interactive=False)

                with gr.Tab("Transcript"):
                    transcript = gr.Textbox(
                        label="Speech Transcript",
                        lines=5,
                        interactive=False
                    )

                with gr.Tab("Analysis"):
                    analysis = gr.Textbox(
                        label="Speech Analysis",
                        lines=8,
                        interactive=False
                    )

                with gr.Tab("Improvements"):
                    improvements = gr.Textbox(
                        label="Improvement Suggestions",
                        lines=8,
                        interactive=False
                    )

                with gr.Tab("Improved Audio"):
                    improved_audio = gr.Audio(
                        label="Improved Speech",
                        interactive=False
                    )

        # Event handlers
        process_btn.click(
            fn=process_speech,
            inputs=[audio_input, voice_selection, analysis_depth, improvement_focus],
            outputs=[improved_audio, transcript, analysis, improvements, status]
        )

        # Examples
        gr.Markdown("## 📝 Example Usage")
        gr.Examples(
            examples=[
                ["Record a short speech about your goals"],
                ["Upload a presentation excerpt"],
                ["Practice a job interview response"]
            ],
            inputs=[gr.Textbox(label="Try these scenarios", visible=False)],
            label="Sample Use Cases"
        )

    return demo

if __name__ == "__main__":
    logger.info(f"Starting Pitch Perfect Frontend in {Config.ENVIRONMENT} mode")
    logger.info(f"Server will run on {Config.SERVER_NAME}:{Config.SERVER_PORT}")

    demo = create_interface()
    demo.launch(
        server_name=Config.SERVER_NAME,
        server_port=Config.SERVER_PORT,
        share=Config.SHARE,
        show_error=True,
        auth=None,  # Add authentication if needed
        ssl_verify=False if Config.ENVIRONMENT == "development" else True
    )
