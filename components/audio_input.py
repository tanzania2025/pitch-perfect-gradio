import gradio as gr
from config import Config

def create_audio_input():
    """Create audio input component with validation"""

    def validate_audio(audio_file):
        if audio_file is None:
            return "Please upload an audio file"

        # Add validation logic here
        return "Audio file is valid"

    audio_input = gr.Audio(
        label="Upload Audio File",
        type="filepath",
        format="wav"
    )

    return audio_input
