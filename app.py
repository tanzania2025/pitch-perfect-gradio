import gradio as gr
import os
import sys
from typing import Dict, Any, Optional

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from api_client import PitchPerfectAPI
    from config import Config
    from components.results_display import create_results_display, format_results_from_backend
except ImportError as e:
    print(f"Import error: {e}")
    print("Please make sure all component files are created correctly.")
    sys.exit(1)

# Initialize API client
api_client = PitchPerfectAPI()

def create_empty_results(error_message):
    """Create empty results tuple for error cases"""
    return (
        error_message,  # status
        "",            # session_info
        "",            # transcript
        {},            # transcript_details
        {},            # processing_metrics
        "",            # sentiment_summary
        None,          # sentiment_chart
        {},            # sentiment_details
        "",            # tonal_summary
        None,          # tonal_chart
        {},            # prosodic_details
        {},            # voice_quality_details
        "",            # improved_text
        "",            # issues_found
        "",            # improvement_feedback
        {},            # prosody_guide
        "",            # ssml_markup
        None,          # improved_audio
        {},            # synthesis_info
        None,          # metrics_comparison
        None           # timeline_chart
    )

def format_for_gradio_outputs(formatted_results):
    """Convert formatted results to Gradio output tuple"""
    return (
        formatted_results.get('status', ''),
        formatted_results.get('session_info', ''),
        formatted_results.get('transcript', ''),
        formatted_results.get('transcript_details', {}),
        formatted_results.get('processing_metrics', {}),
        formatted_results.get('sentiment_summary', ''),
        formatted_results.get('sentiment_chart'),
        formatted_results.get('sentiment_details', {}),
        formatted_results.get('tonal_summary', ''),
        formatted_results.get('tonal_chart'),
        formatted_results.get('prosodic_details', {}),
        formatted_results.get('voice_quality_details', {}),
        formatted_results.get('improved_text', ''),
        formatted_results.get('issues_found', ''),
        formatted_results.get('improvement_feedback', ''),
        formatted_results.get('prosody_guide', {}),
        formatted_results.get('ssml_markup', ''),
        formatted_results.get('improved_audio'),
        formatted_results.get('synthesis_info', {}),
        formatted_results.get('metrics_comparison'),
        formatted_results.get('timeline_chart')
    )

def safe_get_voice_options() -> list:
    """Safely get voice options with fallback"""
    try:
        voice_data = api_client.get_voice_options()
        voices = voice_data.get("voices", [])
        if not voices:
            return ["Default Voice", "Professional Voice", "Casual Voice"]
        return voices
    except Exception as e:
        print(f"Warning: Could not load voice options: {e}")
        return ["Default Voice", "Professional Voice", "Casual Voice"]

def process_speech(audio_file, voice_selection, analysis_depth, improvement_focus):
    """Main processing function with comprehensive results handling"""

    print(f"Processing audio: {audio_file}")
    print(f"Voice: {voice_selection}")
    print(f"Depth: {analysis_depth}")
    print(f"Focus: {improvement_focus}")

    if audio_file is None:
        return create_empty_results("❌ Please upload an audio file")

    # Validate audio file (basic validation)
    try:
        if hasattr(audio_file, 'name') and audio_file.name:
            file_ext = audio_file.name.lower().split('.')[-1]
            if file_ext not in Config.SUPPORTED_FORMATS:
                return create_empty_results(f"❌ Unsupported file format: {file_ext}")
    except Exception as e:
        print(f"Validation error: {e}")

    # Check backend availability
    try:
        if not api_client.health_check():
            return create_empty_results("❌ Backend service is unavailable. Please ensure your backend is running.")
    except Exception as e:
        print(f"Health check error: {e}")
        return create_empty_results("❌ Could not connect to backend service")

    # Prepare settings to match backend expectations
    settings = {
        "voice_selection": voice_selection,
        "analysis_depth": analysis_depth,
        "improvement_focus": improvement_focus
    }

    # Process audio
    try:
        with open(audio_file, 'rb') as f:
            result = api_client.process_audio(f, settings)

        if "error" in result:
            return create_empty_results(f"❌ Processing error: {result['error']}")

        # Format all results using the comprehensive formatter
        formatted_results = format_results_from_backend(result)
        formatted_results['status'] = "✅ Processing completed successfully!"
        
        return format_for_gradio_outputs(formatted_results)

    except Exception as e:
        error_msg = f"❌ Unexpected error during processing: {str(e)}"
        print(f"Processing error: {e}")
        return create_empty_results(error_msg)

def create_interface():
    """Create the main Gradio interface"""

    # Initialize session state (placeholder for future use)
    try:
        # Session state would be initialized here if needed
        pass
    except Exception as e:
        print(f"Session state initialization error: {e}")

    # Get voice options safely
    voice_choices = safe_get_voice_options()

    # Custom CSS
    custom_css = """
    <style>
    .gradio-container {
        max-width: 1200px !important;
    }
    .main-header {
        text-align: center;
        color: #FF6B6B;
        margin-bottom: 2rem;
    }
    .section-header {
        color: #4ECDC4;
        border-bottom: 2px solid #4ECDC4;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    </style>
    """

    with gr.Blocks(
        title=Config.APP_TITLE,
        theme=gr.themes.Soft(),
        css=custom_css
    ) as demo:

        gr.HTML(f"""
        <div class="main-header">
            <h1>🎤 {Config.APP_TITLE}</h1>
            <p>{Config.APP_DESCRIPTION}</p>
        </div>
        """)

        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML('<h2 class="section-header">🎤 Audio Input</h2>')

                # Audio input
                audio_input = gr.Audio(
                    label="Upload or Record Audio",
                    type="filepath"
                )

                gr.HTML('<h3 class="section-header">⚙️ Settings</h3>')

                # Settings - matching what backend expects
                voice_selection = gr.Dropdown(
                    choices=voice_choices,
                    value=voice_choices[0],
                    label="TTS Voice Style",
                    allow_custom_value=False
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

                # Process button
                process_btn = gr.Button(
                    "🚀 Analyze Speech",
                    variant="primary",
                    size="lg"
                )

            with gr.Column(scale=2):
                gr.HTML('<h2 class="section-header">📊 Results</h2>')

                # Create comprehensive results display
                results_components = create_results_display()

        # Examples section
        gr.HTML('<h3 style="color: #45B7D1; margin-top: 2rem;">📝 Example Use Cases</h3>')

        with gr.Row():
            gr.Examples(
                examples=[
                    [None, "Default Voice", "Basic", ["Clarity"]],
                    [None, "Professional Voice", "Detailed", ["Confidence", "Tone"]],
                    [None, "Casual Voice", "Comprehensive", ["Clarity", "Pace", "Emotion"]]
                ],
                inputs=[audio_input, voice_selection, analysis_depth, improvement_focus],
                label="Try these settings combinations"
            )

        # Event handlers - now handling all result components
        process_btn.click(
            fn=process_speech,
            inputs=[audio_input, voice_selection, analysis_depth, improvement_focus],
            outputs=[
                results_components['status'],
                results_components['session_info'],
                results_components['transcript'],
                results_components['transcript_details'],
                results_components['processing_metrics'],
                results_components['sentiment_summary'],
                results_components['sentiment_chart'],
                results_components['sentiment_details'],
                results_components['tonal_summary'],
                results_components['tonal_chart'],
                results_components['prosodic_details'],
                results_components['voice_quality_details'],
                results_components['improved_text'],
                results_components['issues_found'],
                results_components['improvement_feedback'],
                results_components['prosody_guide'],
                results_components['ssml_markup'],
                results_components['improved_audio'],
                results_components['synthesis_info'],
                results_components['metrics_comparison'],
                results_components['timeline_chart']
            ],
            show_progress=True
        )

        # Footer
        gr.HTML("""
        <div style="text-align: center; margin-top: 3rem; padding: 1rem; color: #666;">
            <p>🎯 Pitch Perfect - AI-Powered Speech Improvement System</p>
            <p>Upload audio → Get analysis → Improve your communication skills</p>
        </div>
        """)

    return demo

def main():
    """Main application entry point"""

    print("🚀 Starting Pitch Perfect Gradio Frontend...")
    print("=" * 50)
    print(f"App Title: {Config.APP_TITLE}")
    print(f"Backend URL: {Config.BACKEND_API_URL}")
    print(f"Server Port: {Config.SERVER_PORT}")
    print("=" * 50)

    # Test backend connection
    print("🔍 Testing backend connection...")
    if api_client.health_check():
        print("✅ Backend is accessible")
    else:
        print("⚠️ Backend is not accessible - app will run but processing will fail")
        print(f"   Make sure your backend is running at: {Config.BACKEND_API_URL}")

    # Create and launch interface
    try:
        demo = create_interface()
        print("🌐 Launching Gradio interface...")

        demo.launch(
            server_name=Config.SERVER_NAME,
            server_port=Config.SERVER_PORT,
            share=Config.SHARE,
            show_error=True
        )

    except Exception as e:
        print(f"❌ Failed to launch application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
