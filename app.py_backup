import gradio as gr
import os
import sys
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from api_client import PitchPerfectAPI
    from config import Config
    from components.results_display import cleanup_temp_audio_files, format_results_from_backend
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error("Please make sure all component files are created correctly.")
    sys.exit(1)

# Initialize API client
api_client = PitchPerfectAPI()

# Example scripts
EXAMPLE_SCRIPTS = {
    "Professional Script": """Good morning, team. Today I'd like to discuss our quarterly performance and the strategic initiatives we're implementing for the upcoming fiscal year. Our revenue has increased by fifteen percent compared to last quarter, demonstrating the effectiveness of our customer-centric approach. Moving forward, we'll be focusing on three key areas: enhancing our digital infrastructure, expanding our market presence in emerging territories, and investing in employee development programs. These initiatives will position us competitively in the marketplace while ensuring sustainable growth. I believe that with our collective expertise and commitment to excellence, we can achieve our ambitious targets. The data shows promising trends in customer satisfaction and retention rates, which validates our strategic direction. Let's maintain this momentum and continue delivering exceptional value to our stakeholders.""",

    "Funny Script": """So I went to the grocery store yesterday, and I swear it's like entering a parallel universe where common sense goes to die. First, I spent ten minutes looking for the milk, which apparently decided to relocate itself to the opposite end of the store since my last visit. Then I encountered the self-checkout machine, which I'm convinced was designed by someone who's never actually bought groceries. It kept asking me to place the item in the bagging area, but when I did, it yelled at me for having an unexpected item. I'm standing there arguing with a machine about whether my bananas are actually bananas. The highlight was when it asked if I wanted to donate to charity, and I accidentally said yes out loud, causing the elderly gentleman behind me to think I was talking to him. Technology, folks – making simple tasks complicated since forever!""",

    "Casual Script": """Hey everyone! Hope you're all doing well. I wanted to share something pretty cool that happened to me this week. You know how we're always talking about trying new things and stepping out of our comfort zones? Well, I finally decided to take that cooking class I've been putting off for months. I was honestly a bit nervous at first because I can barely make toast without setting off the smoke alarm. But it turned out to be such an amazing experience! The instructor was super patient, and I learned how to make this incredible pasta dish from scratch. The best part was meeting other people who were just as clueless as me in the kitchen. We all laughed about our cooking disasters and shared tips. It really reminded me how much fun it can be to learn something new, even if you're terrible at it initially. I'm definitely going back next week!""",

    "Presentation Script": """Welcome to our comprehensive overview of sustainable energy solutions for modern businesses. Climate change represents one of the most pressing challenges of our time, and organizations across all sectors must adapt their operations to meet evolving environmental standards. Today's presentation will explore three fundamental approaches to sustainable energy implementation: renewable energy adoption, energy efficiency optimization, and carbon footprint reduction strategies. Research indicates that companies investing in sustainable practices experience significant long-term cost savings while enhancing their brand reputation among environmentally conscious consumers. We'll examine real-world case studies demonstrating successful transitions to green energy systems, analyze the financial implications of various sustainable technologies, and provide actionable recommendations for immediate implementation. Our goal is to equip you with the knowledge necessary to make informed decisions about your organization's energy future while contributing to global sustainability efforts.""",

    "Storytelling Script": """Once upon a time, in a small village nestled between rolling hills and whispering forests, there lived an old clockmaker named Henrik. His workshop was filled with the gentle ticking of countless timepieces, each one telling its own story through the rhythm of passing moments. One peculiar autumn morning, Henrik discovered something extraordinary – a clock that ticked backwards, its hands moving counterclockwise with deliberate precision. As he examined this mysterious timepiece, he noticed that with each backward tick, he could glimpse fragments of memories from days gone by. The clock showed him his childhood adventures, his first love, the day he opened his workshop, and countless precious moments he thought were lost forever. Henrik realized that this magical clock wasn't just measuring time; it was preserving the beautiful tapestry of human experience. From that day forward, he understood that every tick forward was just as precious as every memory from the past, and that time itself was the most valuable gift of all."""
}

def create_empty_results(error_message):
    """Create empty results tuple for error cases"""
    return (
        error_message,  # status
        "",            # transcript
        {},            # transcript_details
        "",            # sentiment_summary
        None,          # sentiment_chart
        {},            # sentiment_details
        "",            # tonal_summary
        None,          # tonal_chart
        {},            # voice_quality_details
        "",            # improved_text
        "",            # improvement_feedback
        {},            # prosody_guide
        None,          # improved_audio
        {},            # synthesis_info
        None,          # metrics_comparison
        None           # timeline_chart
    )

def format_for_gradio_outputs(formatted_results):
    """Convert formatted results to Gradio output tuple"""
    return (
        formatted_results.get('status', ''),
        formatted_results.get('transcript', ''),
        formatted_results.get('transcript_details', {}),
        formatted_results.get('sentiment_summary', ''),
        formatted_results.get('sentiment_chart'),
        formatted_results.get('sentiment_details', {}),
        formatted_results.get('tonal_summary', ''),
        formatted_results.get('tonal_chart'),
        formatted_results.get('voice_quality_details', {}),
        formatted_results.get('improved_text', ''),
        formatted_results.get('improvement_feedback', ''),
        formatted_results.get('prosody_guide', {}),
        formatted_results.get('improved_audio'),
        formatted_results.get('synthesis_info', {}),
        formatted_results.get('metrics_comparison'),
        formatted_results.get('timeline_chart')
    )

def safe_get_voice_options() -> tuple:
    """Safely get voice options with fallback"""
    try:
        voice_data = api_client.get_voice_options()
        voices = voice_data.get("voices", [])
        if not voices:
            voice_choices = ["Default Voice", "Professional Voice", "Casual Voice"]
            voice_mapping = {name: None for name in voice_choices}
            return voice_choices, voice_mapping

        # Extract voice names for dropdown and create mapping
        voice_choices = []
        voice_mapping = {}

        for voice in voices:
            # Include description in display name for better voice selection
            description = voice.get('description', '').strip()
            if voice['category'] == 'premade':
                if description:
                    display_name = f"{voice['name']} - {description}"
                else:
                    display_name = f"{voice['name']}"
            elif voice['category'] == 'cloned':
                if description:
                    display_name = f"{voice['name']} (Cloned) - {description}"
                else:
                    display_name = f"{voice['name']} (Cloned)"
            else:
                if description:
                    display_name = f"{voice['name']} ({voice['category']}) - {description}"
                else:
                    display_name = f"{voice['name']} ({voice['category']})"
            
            voice_choices.append(display_name)
            voice_mapping[display_name] = voice['voice_id']

        logger.info("="*60)
        logger.info("[STARTUP] VOICE OPTIONS LOADED:")
        logger.info(f"  Total voices loaded: {len(voice_choices)}")
        logger.info("  Sample voices:")
        for i, (display_name, voice_id) in enumerate(list(voice_mapping.items())[:3]):
            logger.info(f"    {i+1}. '{display_name}' -> ID: {voice_id}")
        logger.info("="*60)
        return voice_choices, voice_mapping
    except Exception as e:
        logger.warning(f"Could not load voice options: {e}")
        voice_choices = ["Default Voice", "Professional Voice", "Casual Voice"]
        voice_mapping = {name: None for name in voice_choices}
        return voice_choices, voice_mapping

# Global voice mapping
voice_choices, voice_id_mapping = safe_get_voice_options()

def update_text_input(script_choice):
    """Update text input based on selected script"""
    if script_choice and script_choice in EXAMPLE_SCRIPTS:
        return EXAMPLE_SCRIPTS[script_choice]
    return ""

def process_speech(audio_file, text_input, voice_selection, analysis_depth, improvement_focus, progress=gr.Progress()):
    """Main processing function with comprehensive results handling"""
    cleanup_temp_audio_files()
    # Show loading progress
    progress(0.1, desc="Starting analysis...")

    logger.info(f"🎤 Processing audio: {audio_file}")
    logger.info(f"📝 Text input: {text_input[:100]}..." if text_input else "No text")
    logger.info(f"🔊 Voice: {voice_selection}")
    logger.info(f"🔍 Depth: {analysis_depth}")
    logger.info(f"🎯 Focus: {improvement_focus}")

    if audio_file is None and not text_input:
        return create_empty_results("❌ Please upload an audio file or provide text input")

    progress(0.2, desc="Validating input...")

    # Validate audio file if provided
    if audio_file:
        try:
            if hasattr(audio_file, 'name') and audio_file.name:
                file_ext = audio_file.name.lower().split('.')[-1]
                if file_ext not in Config.SUPPORTED_FORMATS:
                    return create_empty_results(f"❌ Unsupported file format: {file_ext}")
        except Exception as e:
            logger.error(f"Validation error: {e}")

    progress(0.3, desc="Connecting to backend...")

    # Check backend availability
    try:
        if not api_client.health_check():
            return create_empty_results("❌ Backend service is unavailable. Please ensure your backend is running.")
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return create_empty_results("❌ Could not connect to backend service")

    progress(0.5, desc="Processing audio/text...")

    # Get voice_id from the mapping
    voice_id = voice_id_mapping.get(voice_selection)

    logger.info("="*60)
    logger.info("[FRONTEND] PROCESSING REQUEST:")
    logger.info(f"  Selected voice display name: '{voice_selection}'")
    logger.info(f"  Mapped voice_id: {voice_id}")
    logger.info(f"  Analysis depth: {analysis_depth}")
    logger.info(f"  Improvement focus: {improvement_focus}")
    logger.info(f"  Text input provided: {bool(text_input)}")
    logger.info(f"  Available voice mappings: {len(voice_id_mapping)} total")
    
    # Debug: Show all available mappings
    logger.info("  All voice mappings:")
    for display_name, vid in voice_id_mapping.items():
        logger.info(f"    '{display_name}' -> '{vid}'")
    
    # Check if voice_selection exists in mapping
    if voice_selection not in voice_id_mapping:
        logger.warning(f"  WARNING: Voice selection '{voice_selection}' not found in mapping!")
        logger.warning(f"  Available keys: {list(voice_id_mapping.keys())}")
    
    logger.info("="*60)

    # Prepare settings
    settings = {
        "voice_selection": voice_selection,
        "voice_id": voice_id,  # Pass the actual voice_id
        "analysis_depth": analysis_depth,
        "improvement_focus": improvement_focus,
        "text_input": text_input if text_input else None
    }
    
    # Double-check voice_id before sending
    if not voice_id:
        logger.warning(f"[FRONTEND] WARNING: voice_id is None/empty for selection '{voice_selection}'")
        # Try to refresh voice mappings in case they're stale
        try:
            new_choices, new_mapping = safe_get_voice_options()
            voice_id = new_mapping.get(voice_selection)
            if voice_id:
                logger.info(f"[FRONTEND] Found voice_id after refresh: {voice_id}")
                settings["voice_id"] = voice_id
            else:
                logger.error(f"[FRONTEND] Still no voice_id after refresh for '{voice_selection}'")
        except Exception as e:
            logger.error(f"[FRONTEND] Error refreshing voice options: {e}")

    # Process audio or text
    try:
        if audio_file:
            with open(audio_file, 'rb') as f:
                result = api_client.process_audio(f, settings)
        else:
            result = api_client.process_text(settings)

        progress(0.8, desc="Analyzing results...")

        if "error" in result:
            return create_empty_results(f"❌ Processing error: {result['error']}")

        progress(0.9, desc="Formatting results...")

        # Format results
        formatted_results = format_results_from_backend(result)

        # Create a prettier status with loading bar effect
        status_html = """
        <div style="background: #e8f5e8; border: 1px solid #4caf50; border-radius: 8px; padding: 15px; margin: 10px 0;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="color: #4caf50; font-size: 18px;">✅</span>
                <span style="color: #2e7d32; font-weight: bold;">Processing completed successfully!</span>
            </div>
            <div class="loading-bar" style="background: linear-gradient(90deg, #4caf50, #8bc34a); height: 4px; border-radius: 2px; margin-top: 8px;"></div>
        </div>
        """
        formatted_results['status'] = status_html

        progress(1.0, desc="Complete!")

        return format_for_gradio_outputs(formatted_results)

    except Exception as e:
        error_msg = f"❌ Unexpected error during processing: {str(e)}"
        logger.error(f"Processing error: {e}")
        return create_empty_results(error_msg)

def create_interface():
    """Create the main Gradio interface"""

    # Custom CSS
    custom_css = """
    <style>
    .gradio-container {
        max-width: 1000px !important;
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
    .loading-bar {
        background: linear-gradient(90deg, #4ECDC4, #45B7D1, #96CEB4);
        background-size: 200% 200%;
        animation: gradient 2s ease infinite;
        height: 4px;
        border-radius: 2px;
        margin: 10px 0;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    #fixed-textbox textarea {
    resize: vertical;      /* allow manual resize if you want, or set to 'none' */
    overflow-y: auto;      /* enable vertical scroll */
    max-height: 150px;     /* same as 5 lines roughly */
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

        # Audio Input + Example Scripts side by side
        with gr.Row():
            with gr.Column():
                gr.HTML('<h2 class="section-header">🎤 Audio Input</h2>')
                audio_input = gr.Audio(
                    label="Upload or Record Audio",
                    type="filepath"
                )
            with gr.Column():
                gr.HTML('<h3 class="section-header">📝 Example Scripts</h3>')
                script_dropdown = gr.Dropdown(
                    choices=list(EXAMPLE_SCRIPTS.keys()),
                    label="Select Example Script",
                    value=None
                )
                text_input = gr.Textbox(
                    label="Text Input (Optional)",
                    placeholder="Enter your text here or select an example script above...",
                    lines=5,          # fixed visible lines
                    max_lines=5,      # prevent auto-expansion
                    elem_id="fixed-textbox"
                )



        # Settings split into two sides
        gr.HTML('<h3 class="section-header">⚙️ Settings</h3>')
        with gr.Row():
            with gr.Column():
                voice_selection = gr.Dropdown(
                    choices=voice_choices,
                    value=voice_choices[0] if voice_choices else "Default Voice",
                    label="TTS Voice Style"
                )
            with gr.Column():
                improvement_focus = gr.CheckboxGroup(
                    choices=["Clarity", "Tone", "Pace", "Confidence", "Emotion"],
                    value=["Clarity", "Tone"],
                    label="Improvement Focus"
                )
                analysis_depth = gr.Radio(
                    choices=["Basic", "Detailed", "Comprehensive"],
                    value="Detailed",
                    label="Analysis Depth"
                )

        # Example Use Cases (moved above settings)
        gr.HTML('<h3 style="color: #45B7D1; margin-top: 1rem;">📝 Example Use Cases</h3>')
        with gr.Row():
            gr.Examples(
                examples=[
                    [None, None, voice_choices[0] if voice_choices else "Default Voice", "Basic", ["Clarity"]],
                    [None, None, voice_choices[1] if len(voice_choices) > 1 else "Default Voice", "Detailed", ["Confidence", "Tone"]],
                    [None, None, voice_choices[2] if len(voice_choices) > 2 else "Default Voice", "Comprehensive", ["Clarity", "Pace", "Emotion"]]
                ],
                inputs=[audio_input, text_input, voice_selection, analysis_depth, improvement_focus],
                label="Try these settings combinations"
            )



        # Process button
        process_btn = gr.Button(
            "🚀 Analyze Speech",
            variant="primary",
            size="lg"
        )

        # Results Section
        gr.HTML('<h2 class="section-header">📊 Results</h2>')
        status_output = gr.HTML(label="Processing Status")

        # Transcript, Metrics, and Audio Results side by side
        with gr.Row():
            with gr.Column():
                gr.HTML('<h3 class="section-header">📝 Transcript & Metrics</h3>')
                transcript_output = gr.Textbox(label="Transcript", lines=3)
                gr.HTML('<h3 class="section-header">🔊 Audio Results</h3>')
                improved_audio_output = gr.Audio(label="Improved Audio")
                synthesis_info_output = gr.JSON(label="Synthesis Info", visible=False)

            with gr.Column():
                gr.HTML('<h3 class="section-header">🔊 Feedback</h3>')
                improved_text_output = gr.Textbox(label="Improved Text", lines=5)
                improvement_feedback_output = gr.Textbox(label="Improvement Feedback", lines=5)

        # Analysis Sections
        with gr.Row():
            with gr.Column():
                gr.HTML('<h3 class="section-header">🎭 Sentiment Analysis</h3>')
                sentiment_summary_output = gr.Textbox(label="Sentiment Summary", lines=3)
                sentiment_chart_output = gr.Plot(label="Sentiment Chart")


            with gr.Column():
                gr.HTML('<h3 class="section-header">🎵 Voice & Tonal Analysis</h3>')
                tonal_summary_output = gr.Textbox(label="Tonal Summary", lines=3)
                tonal_chart_output = gr.Plot(label="Tonal Chart")



        with gr.Accordion("📈 Visual Analysis ▼", open=False):
            metrics_comparison_output = gr.Plot(label="Metrics Comparison")
            timeline_chart_output = gr.Plot(label="Timeline Analysis")

        # Hidden components for data that's not displayed
        transcript_details_output = gr.JSON(visible=False)
        sentiment_details_output = gr.JSON(visible=False)
        voice_quality_details_output = gr.JSON(visible=False)
        prosody_guide_output = gr.JSON(visible=False)

        # Script dropdown event
        script_dropdown.change(
            fn=update_text_input,
            inputs=[script_dropdown],
            outputs=[text_input]
        )

        # Process button event
        process_btn.click(
            fn=process_speech,
            inputs=[audio_input, text_input, voice_selection, analysis_depth, improvement_focus],
            outputs=[
                status_output,
                transcript_output,
                transcript_details_output,
                sentiment_summary_output,
                sentiment_chart_output,
                sentiment_details_output,
                tonal_summary_output,
                tonal_chart_output,
                voice_quality_details_output,
                improved_text_output,
                improvement_feedback_output,
                prosody_guide_output,
                improved_audio_output,
                synthesis_info_output,
                metrics_comparison_output,
                timeline_chart_output
            ],
            show_progress=True
        )

        # Footer
        gr.HTML("""
        <div style="text-align: center; margin-top: 3rem; padding: 1rem; color: #666;">
            <p>🎯 Pitch Perfect - AI-Powered Speech Improvement System</p>
            <p>Upload audio or enter text → Get analysis → Improve your communication skills</p>
        </div>
        """)

    return demo

def main():
    """Main application entry point"""

    logger.info("🚀 Starting Pitch Perfect Gradio Frontend...")
    logger.info("=" * 60)
    logger.info(f"📱 App Title: {Config.APP_TITLE}")
    logger.info(f"🌐 Backend API URL: {Config.BACKEND_API_URL}")
    logger.info(f"🚪 Server Port: {Config.SERVER_PORT}")
    logger.info(f"📍 Server Name: {Config.SERVER_NAME}")
    logger.info("=" * 60)

    # Test backend connection
    logger.info("🔍 Testing backend connection...")
    if api_client.health_check():
        logger.info("✅ Backend is accessible")
    else:
        logger.warning("⚠️ Backend is not accessible - app will run but processing will fail")
        logger.warning(f"   Make sure your backend is running at: {Config.BACKEND_API_URL}")

    # Create and launch interface
    try:
        demo = create_interface()
        logger.info("🌐 Launching Gradio interface...")

        demo.launch(
            server_name=Config.SERVER_NAME,
            server_port=Config.SERVER_PORT,
            share=Config.SHARE,
            show_error=True
        )

    except Exception as e:
        logger.error(f"❌ Failed to launch application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
