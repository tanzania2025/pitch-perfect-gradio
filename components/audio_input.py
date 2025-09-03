import gradio as gr
from config import Config

def create_audio_input():
    """Create comprehensive audio input component with validation and options"""

    with gr.Column():
        # Input method selection
        gr.Markdown("### 🎤 Choose Your Input Method")

        input_method = gr.Radio(
            choices=["Upload File", "Record Audio", "Use Sample"],
            value="Upload File",
            label="Input Method",
            info="Select how you want to provide your audio"
        )

        # File upload section
        with gr.Group(visible=True) as upload_group:
            audio_upload = gr.Audio(
                label="Upload Audio File",
                type="filepath",
                format="wav",
                show_label=True
            )

            # File information
            gr.Markdown(f"""
            **📋 Upload Requirements:**
            - Supported formats: {', '.join(Config.SUPPORTED_FORMATS)}
            - Maximum duration: {Config.MAX_AUDIO_DURATION//60} minutes
            - Maximum file size: 25MB
            - Recommended: Clear audio with minimal background noise
            """)

        # Recording section (placeholder for now)
        with gr.Group(visible=False) as record_group:
            gr.Markdown("🎙️ **Audio Recording**")
            gr.Info("Click the record button below to start recording your speech")

            # Note: This is a placeholder - actual recording implementation would need
            # additional components or custom JavaScript
            record_placeholder = gr.Textbox(
                value="Recording feature will be implemented with audio-recorder component",
                label="Recording Status",
                interactive=False
            )

            gr.Markdown("""
            **🎯 Recording Tips:**
            - Speak clearly and at normal pace
            - Keep 6-12 inches from microphone
            - Record in a quiet environment
            - Aim for 30 seconds to 3 minutes
            """)

        # Sample audio section
        with gr.Group(visible=False) as sample_group:
            gr.Markdown("📝 **Sample Audio Files**")
            gr.Info("Choose from pre-recorded samples to test the system")

            sample_choice = gr.Radio(
                choices=[
                    "Business Presentation",
                    "Casual Conversation",
                    "Public Speaking",
                    "Interview Response"
                ],
                label="Sample Type",
                info="Select a sample that matches your use case"
            )

            sample_audio_display = gr.Audio(
                label="Sample Audio Preview",
                interactive=False
            )

        # Audio validation feedback
        validation_status = gr.Textbox(
            label="Audio Validation",
            interactive=False,
            visible=False
        )

        # Advanced options (collapsible)
        with gr.Accordion("🔧 Advanced Audio Options", open=False):
            audio_preprocessing = gr.Checkbox(
                label="Apply noise reduction",
                value=True,
                info="Automatically reduce background noise"
            )

            normalize_volume = gr.Checkbox(
                label="Normalize audio volume",
                value=True,
                info="Adjust volume to optimal levels"
            )

            trim_silence = gr.Checkbox(
                label="Trim silence from start/end",
                value=True,
                info="Remove silent portions at beginning and end"
            )

    # Event handlers for input method switching
    def toggle_input_groups(method):
        """Toggle visibility of input groups based on selected method"""
        return (
            gr.Group(visible=(method == "Upload File")),
            gr.Group(visible=(method == "Record Audio")),
            gr.Group(visible=(method == "Use Sample"))
        )

    input_method.change(
        fn=toggle_input_groups,
        inputs=[input_method],
        outputs=[upload_group, record_group, sample_group]
    )

    # Sample audio loading
    def load_sample_audio(sample_type):
        """Load sample audio based on selection"""
        # This would load actual sample files in a real implementation
        sample_files = {
            "Business Presentation": "samples/business_presentation.wav",
            "Casual Conversation": "samples/casual_conversation.wav",
            "Public Speaking": "samples/public_speaking.wav",
            "Interview Response": "samples/interview_response.wav"
        }

        # For now, return placeholder
        return f"Sample audio: {sample_type} (placeholder)"

    sample_choice.change(
        fn=load_sample_audio,
        inputs=[sample_choice],
        outputs=[sample_audio_display]
    )

    # Return all components that need to be accessed externally
    return {
        'input_method': input_method,
        'audio_upload': audio_upload,
        'validation_status': validation_status,
        'audio_preprocessing': audio_preprocessing,
        'normalize_volume': normalize_volume,
        'trim_silence': trim_silence,
        'sample_choice': sample_choice,
        'sample_audio_display': sample_audio_display
    }

def validate_audio_input(audio_file, method="Upload File"):
    """Validate the audio input and return status"""

    if method == "Use Sample":
        return "✅ Sample audio loaded successfully"

    if audio_file is None:
        return "❌ Please provide an audio file"

    try:
        # Basic file validation
        import os

        if not os.path.exists(audio_file):
            return "❌ Audio file not found"

        file_size = os.path.getsize(audio_file)

        # Check file size (25MB limit)
        if file_size > 25 * 1024 * 1024:
            return f"❌ File too large: {file_size/(1024*1024):.1f}MB (max 25MB)"

        # Check file extension
        file_ext = os.path.splitext(audio_file)[1].lower()
        supported_exts = [f".{fmt.lower()}" for fmt in Config.SUPPORTED_FORMATS]

        if file_ext not in supported_exts:
            return f"❌ Unsupported format: {file_ext} (supported: {', '.join(supported_exts)})"

        # Additional audio validation could go here
        # (duration check, audio format validation, etc.)

        return f"✅ Audio file validated ({file_size/(1024*1024):.1f}MB)"

    except Exception as e:
        return f"❌ Validation error: {str(e)}"

def get_audio_info(audio_file):
    """Extract basic information about the audio file"""

    if not audio_file:
        return {}

    try:
        import os
        import wave

        info = {
            'filename': os.path.basename(audio_file),
            'size_mb': os.path.getsize(audio_file) / (1024 * 1024),
            'format': os.path.splitext(audio_file)[1].upper()
        }

        # Try to get audio-specific info for WAV files
        if audio_file.lower().endswith('.wav'):
            try:
                with wave.open(audio_file, 'rb') as wav_file:
                    info.update({
                        'duration': wav_file.getnframes() / wav_file.getframerate(),
                        'sample_rate': wav_file.getframerate(),
                        'channels': wav_file.getnchannels(),
                        'sample_width': wav_file.getsampwidth()
                    })
            except:
                # If wave reading fails, that's okay
                pass

        return info

    except Exception as e:
        return {'error': str(e)}

def create_audio_preview(audio_file):
    """Create a preview component for the uploaded audio"""

    if not audio_file:
        return "No audio file provided"

    info = get_audio_info(audio_file)

    if 'error' in info:
        return f"Error reading audio: {info['error']}"

    preview_text = f"""
    **📄 Audio File Information:**
    - Filename: {info.get('filename', 'Unknown')}
    - Size: {info.get('size_mb', 0):.2f} MB
    - Format: {info.get('format', 'Unknown')}
    """

    if 'duration' in info:
        preview_text += f"""
    - Duration: {info['duration']:.1f} seconds
    - Sample Rate: {info.get('sample_rate', 'Unknown')} Hz
    - Channels: {info.get('channels', 'Unknown')}
        """

    return preview_text
