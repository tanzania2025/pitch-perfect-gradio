import base64
import tempfile
import os
from typing import Dict, Any, Optional
import time
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime


def format_results_from_backend(result: Dict[str, Any]) -> Dict[str, Any]:
    """Format backend results for Gradio components"""

    formatted = {
        'status': '',
        'transcript': '',
        'transcript_details': {},
        'sentiment_summary': '',
        'sentiment_chart': None,
        'sentiment_details': {},
        'tonal_summary': '',
        'tonal_chart': None,
        'voice_quality_details': {},
        'improved_text': '',
        'improvement_feedback': '',
        'prosody_guide': {},
        'improved_audio': None,  # This will be the decoded audio
        'synthesis_info': {},
        'metrics_comparison': None,
        'timeline_chart': None
    }

    # Format status
    if result.get('processing_status') == 'completed':
        formatted['status'] = '✅ Processing completed successfully!'
    elif 'error' in result:
        formatted['status'] = f'❌ Error: {result["error"]}'
    else:
        formatted['status'] = '🔄 Processing...'

    # Format transcription results
    if 'transcription' in result:
        trans = result['transcription']
        formatted['transcript'] = trans.get('text', '')
        formatted['transcript_details'] = {
            'language': trans.get('language', 'en'),
            'duration': trans.get('duration', 0),
            'confidence': trans.get('confidence', 0),
            'word_count': len(trans.get('text', '').split())
        }

    # Format sentiment analysis
    if 'sentiment' in result:
        sent = result['sentiment']
        formatted['sentiment_summary'] = format_sentiment_summary(sent)
        formatted['sentiment_details'] = sent
        formatted['sentiment_chart'] = create_sentiment_chart(sent)

    # Format tonal analysis
    if 'tonal' in result:
        tonal = result['tonal']
        problems = tonal.get('acoustic_problems', [])
        formatted['tonal_summary'] = format_tonal_summary(tonal)
        formatted['tonal_chart'] = create_tonal_chart(tonal)
        formatted['voice_quality_details'] = tonal

    # Format LLM improvements
    if 'improvements' in result:
        imp = result['improvements']
        formatted['improved_text'] = imp.get('improved_text', '')

        # Use summary_feedback if available, otherwise build from feedback
        if 'summary_feedback' in imp:
            formatted['improvement_feedback'] = imp['summary_feedback']
        else:
            feedback = imp.get('feedback', {})
            formatted['improvement_feedback'] = feedback.get('summary', 'No feedback available.')

        formatted['prosody_guide'] = imp.get('prosody_guide', {})

    # Handle audio data from synthesis results
    if 'synthesis' in result and result['synthesis'].get('audio_data'):
        try:
            # Decode base64 audio data
            audio_base64 = result['synthesis']['audio_data']
            audio_bytes = base64.b64decode(audio_base64)

            # Option 1: Return bytes directly (Gradio can handle this)
            formatted['improved_audio'] = audio_bytes

            # Option 2: Save to temporary file and return path (more reliable)
            # temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            # temp_file.write(audio_bytes)
            # temp_file.close()
            # formatted['improved_audio'] = temp_file.name

        except Exception as e:
            print(f"Error decoding audio: {e}")
            formatted['improved_audio'] = None

    # Update synthesis info
    if 'synthesis' in result:
        synthesis = result['synthesis']
        formatted['synthesis_info'] = {
            'status': synthesis.get('status', 'unknown'),
            'audio_length': synthesis.get('audio_length', 0),
            'file_size': len(base64.b64decode(synthesis.get('audio_data', ''))) if synthesis.get('audio_data') else 0,
            'format': synthesis.get('audio_format', 'mp3')
        }

    # Add comprehensive visualizations
    formatted['metrics_comparison'] = create_metrics_comparison_chart(result)
    formatted['timeline_chart'] = create_timeline_chart(result)

    return formatted


def create_results_display():
    """Create results display components (if needed for other parts of your app)"""
    # This function can be used to create reusable display components
    pass


def decode_audio_for_gradio(audio_base64: str, audio_format: str = 'mp3') -> Optional[str]:
    """Decode base64 audio and save to temporary file for Gradio"""
    try:
        # Decode base64
        audio_bytes = base64.b64decode(audio_base64)

        # Create temporary file in a dedicated directory
        temp_dir = os.path.join(tempfile.gettempdir(), "pitch_perfect_audio")
        os.makedirs(temp_dir, exist_ok=True)

        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=f'.{audio_format}',
            dir=temp_dir
        )

        temp_file.write(audio_bytes)
        temp_file.close()

        return temp_file.name

    except Exception as e:
        print(f"Error decoding audio for Gradio: {e}")
        return None


def cleanup_temp_audio_files(max_age_hours: int = 1):
    """Clean up old temporary audio files"""
    try:
        temp_dir = os.path.join(tempfile.gettempdir(), "pitch_perfect_audio")
        if not os.path.exists(temp_dir):
            return

        current_time = time.time()
        max_age_seconds = max_age_hours * 3600

        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            if os.path.isfile(file_path):
                if current_time - os.path.getmtime(file_path) > max_age_seconds:
                    try:
                        os.unlink(file_path)
                        print(f"Cleaned up temp file: {filename}")
                    except Exception as e:
                        print(f"Failed to clean up {filename}: {e}")

    except Exception as e:
        print(f"Cleanup error: {e}")


# ============================================================================
# VISUALIZATION FUNCTIONS (Integrated from Script 2)
# ============================================================================

def format_sentiment_summary(sentiment):
    """Create formatted sentiment summary"""
    if not sentiment:
        return "No sentiment analysis available"

    lines = ["🎭 SENTIMENT ANALYSIS SUMMARY", "=" * 40]

    if 'emotion' in sentiment:
        lines.append(f"Primary Emotion: **{sentiment['emotion'].title()}**")
    if 'confidence' in sentiment:
        lines.append(f"Confidence: **{sentiment['confidence']:.1%}**")
    if 'sentiment' in sentiment:
        lines.append(f"Overall Sentiment: **{sentiment['sentiment'].title()}**")
    if 'valence' in sentiment and 'arousal' in sentiment:
        lines.append(f"Valence: {sentiment['valence']:.2f} | Arousal: {sentiment['arousal']:.2f}")

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

    # Prosodic features
    prosodic = tonal.get('prosodic_features', {})
    if prosodic:
        lines.append("\n🎼 PROSODIC FEATURES:")
        for key, value in prosodic.items():
            if isinstance(value, (int, float)):
                lines.append(f"  {key.replace('_', ' ').title()}: {value:.2f}")
            else:
                lines.append(f"  {key.replace('_', ' ').title()}: {value}")

    # Voice quality
    voice_quality = tonal.get('voice_quality', {})
    if voice_quality:
        lines.append("\n🎤 VOICE QUALITY:")
        for key, value in voice_quality.items():
            if isinstance(value, (int, float)):
                lines.append(f"  {key.replace('_', ' ').title()}: {value:.2f}")
            else:
                lines.append(f"  {key.replace('_', ' ').title()}: {value}")

    # Acoustic problems
    problems = tonal.get('acoustic_problems', [])
    if problems:
        lines.append("\n⚠️ ISSUES DETECTED:")
        for problem in problems:
            lines.append(f"  • {problem}")

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
            normalized_value = min(max(value, 0), 1) if value <= 1 else value / max(prosodic.values()) if prosodic.values() else 0
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


def create_results_display():
    """Create results display components (if needed for other parts of your app)"""
    # This function can be used to create reusable display components
    pass
