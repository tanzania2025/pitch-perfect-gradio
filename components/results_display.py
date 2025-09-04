import gradio as gr
import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

def create_results_display():
    """Create comprehensive results display with rich formatting for all backend fields"""

    with gr.Column():
        # Status and session info
        with gr.Row():
            status = gr.Textbox(
                label="Processing Status",
                interactive=False,
                placeholder="Upload audio and click 'Analyze Speech' to see results"
            )
            session_info = gr.Textbox(
                label="Session Info",
                interactive=False,
                placeholder="Session details will appear here"
            )

        # Main results in organized tabs
        with gr.Tabs():
            # 1. TRANSCRIPT TAB
            with gr.Tab("📝 Transcript & Metrics"):
                transcript = gr.Textbox(
                    label="Speech Transcript",
                    lines=8,
                    interactive=False,
                    placeholder="Your speech transcript will appear here..."
                )

                # Transcript details
                with gr.Row():
                    with gr.Column():
                        transcript_details = gr.JSON(
                            label="Transcript Details",
                            visible=True
                        )
                    with gr.Column():
                        processing_metrics = gr.JSON(
                            label="Processing Metrics",
                            visible=True
                        )

            # 2. SENTIMENT ANALYSIS TAB
            with gr.Tab("🎭 Sentiment Analysis"):
                with gr.Row():
                    with gr.Column(scale=2):
                        sentiment_summary = gr.Textbox(
                            label="Sentiment Summary",
                            lines=6,
                            interactive=False
                        )
                    with gr.Column(scale=1):
                        sentiment_chart = gr.Plot(
                            label="Emotion Scores",
                            show_label=False
                        )

                sentiment_details = gr.JSON(
                    label="Detailed Sentiment Analysis",
                    visible=True
                )

            # 3. TONAL ANALYSIS TAB
            with gr.Tab("🎵 Voice & Tonal Analysis"):
                with gr.Row():
                    with gr.Column():
                        tonal_summary = gr.Textbox(
                            label="Voice Quality Assessment",
                            lines=8,
                            interactive=False
                        )
                    with gr.Column():
                        tonal_chart = gr.Plot(
                            label="Acoustic Features",
                            show_label=False
                        )

                with gr.Row():
                    prosodic_details = gr.JSON(
                        label="Prosodic Features",
                        visible=True
                    )
                    voice_quality_details = gr.JSON(
                        label="Voice Quality Metrics",
                        visible=True
                    )

            # 4. IMPROVEMENTS TAB
            with gr.Tab("💡 AI Improvements"):
                improved_text = gr.Textbox(
                    label="Improved Text",
                    lines=6,
                    interactive=False,
                    placeholder="AI-enhanced version will appear here..."
                )

                with gr.Row():
                    with gr.Column():
                        issues_found = gr.Textbox(
                            label="Issues Identified",
                            lines=8,
                            interactive=False
                        )
                    with gr.Column():
                        improvement_feedback = gr.Textbox(
                            label="Improvement Suggestions",
                            lines=8,
                            interactive=False
                        )

                with gr.Row():
                    prosody_guide = gr.JSON(
                        label="Prosody Guide",
                        visible=True
                    )
                    ssml_markup = gr.Textbox(
                        label="SSML Markup",
                        lines=6,
                        interactive=False,
                        placeholder="SSML markup will appear here..."
                    )

            # 5. AUDIO RESULTS TAB
            with gr.Tab("🎵 Audio Results"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("**Improved Audio:**")
                        improved_audio = gr.Audio(
                            label="AI-Enhanced Speech",
                            interactive=False
                        )
                    with gr.Column():
                        synthesis_info = gr.JSON(
                            label="Synthesis Details",
                            visible=True
                        )

            # 6. CHARTS & VISUALIZATIONS TAB
            with gr.Tab("📊 Visual Analysis"):
                with gr.Row():
                    metrics_comparison = gr.Plot(
                        label="Metrics Comparison",
                        show_label=False
                    )

                timeline_chart = gr.Plot(
                    label="Processing Timeline",
                    show_label=False
                )

    # Return all components for external access
    return {
        'status': status,
        'session_info': session_info,
        'transcript': transcript,
        'transcript_details': transcript_details,
        'processing_metrics': processing_metrics,
        'sentiment_summary': sentiment_summary,
        'sentiment_chart': sentiment_chart,
        'sentiment_details': sentiment_details,
        'tonal_summary': tonal_summary,
        'tonal_chart': tonal_chart,
        'prosodic_details': prosodic_details,
        'voice_quality_details': voice_quality_details,
        'improved_text': improved_text,
        'issues_found': issues_found,
        'improvement_feedback': improvement_feedback,
        'prosody_guide': prosody_guide,
        'ssml_markup': ssml_markup,
        'improved_audio': improved_audio,
        'synthesis_info': synthesis_info,
        'metrics_comparison': metrics_comparison,
        'timeline_chart': timeline_chart
    }

def format_results_from_backend(result):
    """Format complete backend response for display in all components"""

    formatted = {}

    # Status and session
    formatted['status'] = f"✅ {result.get('processing_status', 'Unknown')}"

    session_info = f"Session: {result.get('session_id', 'N/A')}"
    if result.get('timestamp'):
        session_info += f"\nProcessed: {result['timestamp']}"
    formatted['session_info'] = session_info

    # Transcription
    transcription = result.get('transcription', {})
    formatted['transcript'] = transcription.get('text', 'No transcript available')

    # Transcript details (remove text for cleaner JSON view)
    transcript_details = dict(transcription)
    if 'text' in transcript_details:
        del transcript_details['text']
    formatted['transcript_details'] = transcript_details

    # Processing metrics
    formatted['processing_metrics'] = result.get('metrics', {})

    # Sentiment analysis
    sentiment = result.get('sentiment', {})
    formatted['sentiment_summary'] = format_sentiment_summary(sentiment)
    formatted['sentiment_details'] = sentiment
    formatted['sentiment_chart'] = create_sentiment_chart(sentiment)

    # Tonal analysis
    tonal = result.get('tonal', {})
    formatted['tonal_summary'] = format_tonal_summary(tonal)
    formatted['tonal_chart'] = create_tonal_chart(tonal)
    formatted['prosodic_details'] = tonal.get('prosodic_features', {})
    formatted['voice_quality_details'] = tonal.get('voice_quality', {})

    # Improvements
    improvements = result.get('improvements', {})
    formatted['improved_text'] = improvements.get('improved_text', 'No improvements available')
    formatted['issues_found'] = format_issues(improvements.get('issues', []))
    formatted['improvement_feedback'] = format_feedback(improvements.get('feedback', {}))
    formatted['prosody_guide'] = improvements.get('prosody_guide', {})
    formatted['ssml_markup'] = improvements.get('ssml_markup', '')

    # Audio synthesis
    synthesis = result.get('synthesis', {})
    formatted['synthesis_info'] = synthesis
    formatted['improved_audio'] = result.get('improved_audio_path')

    # Charts
    formatted['metrics_comparison'] = create_metrics_comparison_chart(result)
    formatted['timeline_chart'] = create_timeline_chart(result)

    return formatted

def format_sentiment_summary(sentiment):
    """Create formatted sentiment summary"""
    if not sentiment:
        return "No sentiment analysis available"

    lines = ["🎭 SENTIMENT ANALYSIS SUMMARY", "=" * 40]

    if 'emotion' in sentiment:
        lines.append(f"Primary Emotion: {sentiment['emotion'].title()}")
    if 'confidence' in sentiment:
        lines.append(f"Confidence: {sentiment['confidence']:.1%}")
    if 'sentiment' in sentiment:
        lines.append(f"Overall Sentiment: {sentiment['sentiment'].title()}")

    # Move valence and arousal to tonal summary instead
    # if 'valence' in sentiment and 'arousal' in sentiment:
    #     lines.append(f"Valence: {sentiment['valence']:.2f} | Arousal: {sentiment['arousal']:.2f}")

    if 'emotion_scores' in sentiment:
        lines.append("\n📊 EMOTION BREAKDOWN:")
        for emotion, score in sentiment['emotion_scores'].items():
            lines.append(f"  {emotion.title()}: {score:.1%}")

    return "\n".join(lines)

def format_tonal_summary(tonal):
    """Create formatted tonal analysis summary"""
    if not tonal:
        return "No tonal analysis available"

    lines = ["🎵 VOICE & TONAL ANALYSIS", "=" * 40]

    # Add valence and arousal explanations here
    if 'valence' in tonal or 'arousal' in tonal:
        lines.append("\n🧠 EMOTIONAL DIMENSIONS:")
        if 'valence' in tonal:
            valence = tonal['valence']
            valence_desc = "Positive" if valence > 0.5 else "Negative" if valence < -0.5 else "Neutral"
            lines.append(f"  Valence: {valence:.2f} ({valence_desc})")
            lines.append(f"    → How pleasant/unpleasant your speech sounds")

        if 'arousal' in tonal:
            arousal = tonal['arousal']
            arousal_desc = "High Energy" if arousal > 0.5 else "Low Energy" if arousal < -0.5 else "Moderate Energy"
            lines.append(f"  Arousal: {arousal:.2f} ({arousal_desc})")
            lines.append(f"    → How energetic/calm your speech sounds")

    # Prosodic features as a formatted table
    prosodic = tonal.get('prosodic_features', {})
    if prosodic:
        lines.append("\n🎼 PROSODIC FEATURES:")
        lines.append("Feature                       Value   Level")
        lines.append("-" * 45)

        # Define typical ranges for comparison
        typical_ranges = {
            'mean_hz': (120, 200, 300),
            'std_hz': (20, 50, 100),
            'mean_db': (-40, -20, -10),
            'speaking_rate_wpm': (120, 160, 200),
            'syllables_per_second': (2, 4, 6),
            'pause_ratio': (0.1, 0.3, 0.5),
            'average_pause_duration': (0.3, 0.6, 1.0),
        }

        # Process nested prosodic features
        for category, features in prosodic.items():
            if isinstance(features, dict):
                for key, value in features.items():
                    if isinstance(value, (int, float)):
                        # Create descriptive name
                        clean_key = f"{category.title()} {key.replace('_', ' ').title()}"

                        # Determine level
                        level = "Normal"
                        if key in typical_ranges:
                            low, normal, high = typical_ranges[key]
                            if value < low:
                                level = "Low"
                            elif value > high:
                                level = "High"

                        # Fixed width formatting for perfect alignment
                        lines.append(f"{clean_key:<29} {value:>7.2f}   {level}")

    # Voice quality
    voice_quality = tonal.get('voice_quality', {})
    if voice_quality:
        lines.append("\n🎤 VOICE QUALITY:")
        for key, value in voice_quality.items():
            clean_key = key.replace('_', ' ').title()
            if isinstance(value, (int, float)):
                lines.append(f"  {clean_key}: {value:.2f}")
            else:
                lines.append(f"  {clean_key}: {value}")

    # Acoustic problems - make them user-readable
    problems = tonal.get('acoustic_problems', [])
    if problems:
        lines.append("\n⚠️ ISSUES DETECTED:")
        for problem in problems:
            readable_problem = problem.replace('_', ' ').title()
            lines.append(f"  • {readable_problem}")

    return "\n".join(lines)

def format_issues(issues):
    """Format issues found during analysis"""
    if not issues:
        return "No specific issues identified"

    lines = ["🔍 ISSUES IDENTIFIED:", "=" * 30]

    for i, issue in enumerate(issues, 1):
        if isinstance(issue, dict):
            lines.append(f"{i}. {issue.get('type', 'Unknown')}: {issue.get('description', '')}")
        else:
            lines.append(f"{i}. {issue}")

    return "\n".join(lines)

def format_feedback(feedback):
    """Format improvement feedback"""
    if not feedback:
        return "No feedback available"

    lines = ["💡 IMPROVEMENT SUGGESTIONS:", "=" * 35]

    for key, value in feedback.items():
        if isinstance(value, list):
            lines.append(f"{key.replace('_', ' ').title()}:")
            for item in value:
                lines.append(f"  • {item}")
        else:
            lines.append(f"{key.replace('_', ' ').title()}: {value}")

    return "\n".join(lines)

def create_sentiment_chart(sentiment):
    """Create emotion scores visualization"""
    if not sentiment or 'emotion_scores' not in sentiment:
        return go.Figure().add_annotation(text="No emotion data available", showarrow=False)

    emotions = list(sentiment['emotion_scores'].keys())
    scores = list(sentiment['emotion_scores'].values())

    fig = go.Figure(data=[
        go.Bar(x=emotions, y=scores,
               marker_color='lightblue',
               text=[f"{score:.1%}" for score in scores],
               textposition='auto')
    ])

    fig.update_layout(
        title="Emotion Scores Distribution",
        xaxis_title="Emotions",
        yaxis_title="Confidence",
        yaxis=dict(tickformat=".0%"),
        height=400
    )

    return fig

def create_tonal_chart(tonal):
    """Create tonal features radar chart"""
    if not tonal or 'prosodic_features' not in tonal:
        return go.Figure().add_annotation(text="No tonal data available", showarrow=False)

    prosodic = tonal['prosodic_features']

    # Extract numerical features for radar chart
    features = []
    values = []

    for key, value in prosodic.items():
        if isinstance(value, (int, float)):
            features.append(key.replace('_', ' ').title())
            # Normalize values to 0-1 range for better visualization
            normalized_value = min(max(value, 0), 1) if value <= 1 else value / max(prosodic.values())
            values.append(normalized_value)

    if not features:
        return go.Figure().add_annotation(text="No numerical tonal features available", showarrow=False)

    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=features,
        fill='toself',
        name='Prosodic Features'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=False,
        title="Prosodic Features Analysis",
        height=400
    )

    return fig

def create_metrics_comparison_chart(result):
    """Create metrics comparison chart"""
    metrics = result.get('metrics', {})

    if not metrics:
        return go.Figure().add_annotation(text="No metrics available", showarrow=False)

    # Create comparison of original vs improved
    categories = ['Word Count', 'Issues Found']
    original = [metrics.get('original_word_count', 0), 0]  # Original has 0 issues resolved
    improved = [metrics.get('improved_word_count', 0), metrics.get('issues_found', 0)]

    fig = go.Figure(data=[
        go.Bar(name='Original', x=categories, y=original, marker_color='lightcoral'),
        go.Bar(name='Processed', x=categories, y=improved, marker_color='lightblue')
    ])

    fig.update_layout(
        title="Before vs After Comparison",
        barmode='group',
        height=400
    )

    return fig

def create_timeline_chart(result):
    """Create processing timeline chart"""
    metrics = result.get('metrics', {})
    processing_time = metrics.get('processing_time_seconds', 0)

    if processing_time == 0:
        return go.Figure().add_annotation(text="No timing data available", showarrow=False)

    # Simulate processing stages (in real implementation, you'd get this from backend)
    stages = ['Speech-to-Text', 'Sentiment Analysis', 'Tonal Analysis', 'LLM Processing', 'Audio Synthesis']
    # Estimate time distribution (this would come from actual backend timing)
    stage_times = [processing_time * 0.3, processing_time * 0.1, processing_time * 0.2, processing_time * 0.3, processing_time * 0.1]

    fig = go.Figure(data=[
        go.Bar(x=stages, y=stage_times, marker_color='lightgreen')
    ])

    fig.update_layout(
        title=f"Processing Pipeline Timing (Total: {processing_time:.2f}s)",
        xaxis_title="Processing Stages",
        yaxis_title="Time (seconds)",
        height=400
    )

    return fig
