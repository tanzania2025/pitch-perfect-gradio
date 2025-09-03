import gradio as gr

def create_settings_panel(voice_choices=None):
    """Create comprehensive settings panel for speech processing configuration"""

    if voice_choices is None or len(voice_choices) == 0:
        voice_choices = ["Default Voice", "Professional Voice", "Casual Voice"]

    with gr.Column():
        gr.Markdown("### ⚙️ Processing Configuration")

        # Voice and TTS Settings
        with gr.Group():
            gr.Markdown("**🎤 Voice & Speech Settings**")

            voice_selection = gr.Dropdown(
                choices=voice_choices,
                value=voice_choices[0] if voice_choices else "Default Voice",
                label="TTS Voice",
                info="Select voice for improved speech generation"
            )

            voice_speed = gr.Slider(
                minimum=0.5,
                maximum=2.0,
                step=0.1,
                value=1.0,
                label="Speech Speed",
                info="Adjust playback speed for improved audio"
            )

            voice_pitch = gr.Slider(
                minimum=0.5,
                maximum=2.0,
                step=0.1,
                value=1.0,
                label="Voice Pitch Adjustment",
                info="Fine-tune pitch for improved speech"
            )

        # Analysis Settings
        with gr.Group():
            gr.Markdown("**📊 Analysis Configuration**")

            analysis_depth = gr.Radio(
                choices=["Basic", "Detailed", "Comprehensive"],
                value="Detailed",
                label="Analysis Depth",
                info="Choose level of analysis detail"
            )

            analysis_language = gr.Dropdown(
                choices=[
                    "English (US)",
                    "English (UK)",
                    "English (AU)",
                    "Spanish",
                    "French",
                    "German",
                    "Auto-Detect"
                ],
                value="English (US)",
                label="Language",
                info="Select or auto-detect speech language"
            )

            include_transcription = gr.Checkbox(
                value=True,
                label="Include full transcription",
                info="Generate complete text transcript"
            )

            sentiment_analysis = gr.Checkbox(
                value=True,
                label="Sentiment analysis",
                info="Analyze emotional tone and sentiment"
            )

            tonal_analysis = gr.Checkbox(
                value=True,
                label="Advanced tonal analysis",
                info="Analyze pitch, pace, and vocal patterns"
            )

        # Improvement Focus Areas
        with gr.Group():
            gr.Markdown("**🎯 Improvement Focus Areas**")

            improvement_focus = gr.CheckboxGroup(
                choices=[
                    "Clarity & Articulation",
                    "Tone & Emotion",
                    "Pace & Timing",
                    "Confidence & Authority",
                    "Engagement & Variety",
                    "Grammar & Structure",
                    "Pronunciation",
                    "Volume & Projection"
                ],
                value=["Clarity & Articulation", "Tone & Emotion"],
                label="Areas to Focus On",
                info="Select specific aspects for improvement suggestions"
            )

            improvement_level = gr.Radio(
                choices=["Gentle", "Moderate", "Intensive"],
                value="Moderate",
                label="Improvement Intensity",
                info="How aggressive should the improvements be?"
            )

        # Advanced Processing Options
        with gr.Accordion("🔬 Advanced Options", open=False):

            # AI Model Selection
            model_settings = gr.Group()
            with model_settings:
                gr.Markdown("**🤖 AI Model Configuration**")

                llm_model = gr.Dropdown(
                    choices=["GPT-4", "GPT-3.5-Turbo", "Claude-3", "Local Model"],
                    value="GPT-4",
                    label="Language Model",
                    info="Choose AI model for analysis and suggestions"
                )

                creativity_level = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    step=0.1,
                    value=0.7,
                    label="AI Creativity Level",
                    info="Higher values = more creative suggestions"
                )

            # Audio Processing Options
            audio_processing = gr.Group()
            with audio_processing:
                gr.Markdown("**🎵 Audio Processing**")

                noise_reduction = gr.Checkbox(
                    value=True,
                    label="Apply noise reduction",
                    info="Clean up background noise"
                )

                audio_enhancement = gr.Checkbox(
                    value=True,
                    label="Enhanced audio quality",
                    info="Apply audio enhancement filters"
                )

                normalize_volume = gr.Checkbox(
                    value=True,
                    label="Volume normalization",
                    info="Adjust audio to optimal volume levels"
                )

            # Output Preferences
            output_preferences = gr.Group()
            with output_preferences:
                gr.Markdown("**📤 Output Preferences**")

                detailed_feedback = gr.Checkbox(
                    value=True,
                    label="Detailed written feedback",
                    info="Include comprehensive improvement explanations"
                )

                generate_improved_audio = gr.Checkbox(
                    value=True,
                    label="Generate improved audio",
                    info="Create enhanced version using TTS"
                )

                include_visualizations = gr.Checkbox(
                    value=True,
                    label="Include analysis charts",
                    info="Generate visual analysis plots"
                )

                export_format = gr.Radio(
                    choices=["WAV", "MP3", "FLAC"],
                    value="WAV",
                    label="Audio Export Format",
                    info="Choose format for improved audio"
                )

        # Processing Options Summary
        with gr.Group():
            gr.Markdown("**📋 Processing Summary**")

            processing_preview = gr.Textbox(
                label="Current Configuration",
                lines=3,
                interactive=False,
                placeholder="Configuration summary will appear here..."
            )

            # Estimated processing time
            estimated_time = gr.Textbox(
                label="Estimated Processing Time",
                interactive=False,
                placeholder="Time estimate will appear here..."
            )

    # Function to update processing summary
    def update_processing_summary(depth, focus_areas, voice, improvements):
        """Generate a summary of current processing configuration"""

        summary_parts = []
        summary_parts.append(f"Analysis: {depth}")
        summary_parts.append(f"Voice: {voice}")
        summary_parts.append(f"Focus Areas: {len(focus_areas)} selected")
        summary_parts.append(f"Improvement Level: {improvements}")

        return "\n".join(summary_parts)

    def estimate_processing_time(depth, focus_areas, include_audio):
        """Estimate processing time based on settings"""

        base_time = 30  # Base processing time in seconds

        # Add time based on analysis depth
        depth_multipliers = {"Basic": 1.0, "Detailed": 1.5, "Comprehensive": 2.0}
        time_estimate = base_time * depth_multipliers.get(depth, 1.0)

        # Add time for each focus area
        time_estimate += len(focus_areas) * 10

        # Add time for audio generation
        if include_audio:
            time_estimate += 45

        minutes = int(time_estimate // 60)
        seconds = int(time_estimate % 60)

        if minutes > 0:
            return f"~{minutes}m {seconds}s"
        else:
            return f"~{seconds}s"

    # Update summary when settings change
    analysis_depth.change(
        fn=lambda depth, focus, voice, improvements, include_audio: [
            update_processing_summary(depth, focus, voice, improvements),
            estimate_processing_time(depth, focus, include_audio)
        ],
        inputs=[analysis_depth, improvement_focus, voice_selection, improvement_level, generate_improved_audio],
        outputs=[processing_preview, estimated_time]
    )

    improvement_focus.change(
        fn=lambda depth, focus, voice, improvements, include_audio: [
            update_processing_summary(depth, focus, voice, improvements),
            estimate_processing_time(depth, focus, include_audio)
        ],
        inputs=[analysis_depth, improvement_focus, voice_selection, improvement_level, generate_improved_audio],
        outputs=[processing_preview, estimated_time]
    )

    # Return all components that need external access
    return {
        # Core settings
        'voice_selection': voice_selection,
        'voice_speed': voice_speed,
        'voice_pitch': voice_pitch,
        'analysis_depth': analysis_depth,
        'analysis_language': analysis_language,
        'improvement_focus': improvement_focus,
        'improvement_level': improvement_level,

        # Checkboxes
        'include_transcription': include_transcription,
        'sentiment_analysis': sentiment_analysis,
        'tonal_analysis': tonal_analysis,
        'detailed_feedback': detailed_feedback,
        'generate_improved_audio': generate_improved_audio,
        'include_visualizations': include_visualizations,

        # Advanced options
        'llm_model': llm_model,
        'creativity_level': creativity_level,
        'noise_reduction': noise_reduction,
        'audio_enhancement': audio_enhancement,
        'normalize_volume': normalize_volume,
        'export_format': export_format,

        # Summary components
        'processing_preview': processing_preview,
        'estimated_time': estimated_time
    }

def get_processing_settings(settings_components):
    """Extract all current settings into a dictionary for API calls"""

    # This would extract current values from all components
    # and return them as a structured dictionary for the backend

    settings = {
        'voice': {
            'selection': 'Default Voice',  # Would get from voice_selection.value
            'speed': 1.0,                  # Would get from voice_speed.value
            'pitch': 1.0                   # Would get from voice_pitch.value
        },
        'analysis': {
            'depth': 'Detailed',          # Would get from analysis_depth.value
            'language': 'English (US)',   # Would get from analysis_language.value
            'include_transcription': True,
            'sentiment_analysis': True,
            'tonal_analysis': True
        },
        'improvements': {
            'focus_areas': ['Clarity & Articulation', 'Tone & Emotion'],
            'level': 'Moderate'
        },
        'processing': {
            'llm_model': 'GPT-4',
            'creativity_level': 0.7,
            'noise_reduction': True,
            'audio_enhancement': True,
            'normalize_volume': True
        },
        'output': {
            'detailed_feedback': True,
            'generate_improved_audio': True,
            'include_visualizations': True,
            'export_format': 'WAV'
        }
    }

    return settings

def create_settings_presets():
    """Create preset configurations for common use cases"""

    presets = {
        "Quick Analysis": {
            'analysis_depth': "Basic",
            'improvement_focus': ["Clarity & Articulation"],
            'generate_improved_audio': False,
            'include_visualizations': False
        },
        "Presentation Coach": {
            'analysis_depth': "Comprehensive",
            'improvement_focus': ["Confidence & Authority", "Engagement & Variety", "Pace & Timing"],
            'improvement_level': "Moderate",
            'detailed_feedback': True
        },
        "Language Learning": {
            'analysis_depth': "Comprehensive",
            'improvement_focus': ["Pronunciation", "Clarity & Articulation", "Grammar & Structure"],
            'improvement_level': "Intensive",
            'analysis_language': "Auto-Detect"
        },
        "Interview Prep": {
            'analysis_depth': "Detailed",
            'improvement_focus': ["Confidence & Authority", "Clarity & Articulation", "Tone & Emotion"],
            'improvement_level': "Moderate"
        }
    }

    return presets
