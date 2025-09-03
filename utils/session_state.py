"""
Session state management utilities for the Gradio Pitch Perfect application
"""

import gradio as gr
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime

def initialize_session_state():
    """Initialize all session state variables for the application"""

    # Processing state
    if not hasattr(gr, '_pitch_perfect_session'):
        gr._pitch_perfect_session = {}

    session = gr._pitch_perfect_session

    # Core application state
    if 'initialized' not in session:
        session.update({
            'initialized': True,
            'app_start_time': datetime.now(),
            'processing_history': [],
            'current_audio_file': None,
            'last_processing_result': None,
            'user_preferences': get_default_preferences(),
            'analysis_cache': {},
            'processing_stats': {
                'total_processed': 0,
                'successful_analyses': 0,
                'failed_analyses': 0,
                'total_processing_time': 0.0
            }
        })

    return session

def get_default_preferences():
    """Get default user preferences"""

    return {
        'voice_selection': 'Default Voice',
        'analysis_depth': 'Detailed',
        'improvement_focus': ['Clarity & Articulation', 'Tone & Emotion'],
        'improvement_level': 'Moderate',
        'auto_play_results': True,
        'save_processing_history': True,
        'preferred_language': 'English (US)',
        'audio_format': 'WAV',
        'theme': 'light'
    }

def save_processing_result(audio_file: str, settings: Dict, results: Dict):
    """Save processing result to session history"""

    session = gr._pitch_perfect_session

    processing_entry = {
        'timestamp': datetime.now().isoformat(),
        'audio_file': audio_file,
        'settings': settings.copy(),
        'results': results.copy(),
        'processing_id': f"proc_{int(time.time())}"
    }

    session['processing_history'].append(processing_entry)
    session['last_processing_result'] = processing_entry

    # Update statistics
    stats = session['processing_stats']
    stats['total_processed'] += 1

    if 'error' not in results:
        stats['successful_analyses'] += 1
    else:
        stats['failed_analyses'] += 1

    # Limit history to last 50 entries to prevent memory issues
    if len(session['processing_history']) > 50:
        session['processing_history'] = session['processing_history'][-50:]

    return processing_entry['processing_id']

def get_processing_history(limit: int = 10) -> list:
    """Get recent processing history"""

    session = gr._pitch_perfect_session
    history = session.get('processing_history', [])

    # Return most recent entries
    return history[-limit:] if history else []

def get_last_processing_result() -> Optional[Dict]:
    """Get the last processing result"""

    session = gr._pitch_perfect_session
    return session.get('last_processing_result')

def update_user_preferences(preferences: Dict):
    """Update user preferences in session state"""

    session = gr._pitch_perfect_session
    session['user_preferences'].update(preferences)

    return session['user_preferences']

def get_user_preferences() -> Dict:
    """Get current user preferences"""

    session = gr._pitch_perfect_session
    return session.get('user_preferences', get_default_preferences())

def cache_analysis_result(audio_hash: str, settings_hash: str, result: Dict):
    """Cache analysis result to avoid reprocessing identical requests"""

    session = gr._pitch_perfect_session
    cache_key = f"{audio_hash}_{settings_hash}"

    session['analysis_cache'][cache_key] = {
        'result': result,
        'timestamp': datetime.now().isoformat(),
        'access_count': 1
    }

    # Limit cache size
    if len(session['analysis_cache']) > 100:
        # Remove oldest entries
        sorted_cache = sorted(
            session['analysis_cache'].items(),
            key=lambda x: x[1]['timestamp']
        )
        # Keep newest 50 entries
        session['analysis_cache'] = dict(sorted_cache[-50:])

def get_cached_analysis(audio_hash: str, settings_hash: str) -> Optional[Dict]:
    """Get cached analysis result if available"""

    session = gr._pitch_perfect_session
    cache_key = f"{audio_hash}_{settings_hash}"

    if cache_key in session['analysis_cache']:
        cached_entry = session['analysis_cache'][cache_key]
        cached_entry['access_count'] += 1
        return cached_entry['result']

    return None

def get_processing_statistics() -> Dict:
    """Get processing statistics for the session"""

    session = gr._pitch_perfect_session
    stats = session.get('processing_stats', {})

    # Calculate derived statistics
    total = stats.get('total_processed', 0)
    successful = stats.get('successful_analyses', 0)

    enhanced_stats = stats.copy()
    enhanced_stats.update({
        'success_rate': (successful / total * 100) if total > 0 else 0,
        'average_processing_time': (
            stats.get('total_processing_time', 0) / total
        ) if total > 0 else 0,
        'session_duration': (
            datetime.now() - session.get('app_start_time', datetime.now())
        ).total_seconds() / 60  # in minutes
    })

    return enhanced_stats

def clear_processing_history():
    """Clear all processing history"""

    session = gr._pitch_perfect_session
    session['processing_history'] = []
    session['last_processing_result'] = None
    session['analysis_cache'] = {}

    # Reset statistics
    session['processing_stats'] = {
        'total_processed': 0,
        'successful_analyses': 0,
        'failed_analyses': 0,
        'total_processing_time': 0.0
    }

def export_session_data() -> Dict:
    """Export session data for backup or analysis"""

    session = gr._pitch_perfect_session

    # Create exportable data (excluding sensitive information)
    export_data = {
        'session_info': {
            'start_time': session.get('app_start_time', datetime.now()).isoformat(),
            'export_time': datetime.now().isoformat()
        },
        'statistics': get_processing_statistics(),
        'user_preferences': session.get('user_preferences', {}),
        'processing_history_count': len(session.get('processing_history', [])),
        'cache_entries': len(session.get('analysis_cache', {}))
    }

    return export_data

def create_session_summary() -> str:
    """Create a formatted summary of the current session"""

    stats = get_processing_statistics()
    history = get_processing_history(5)  # Last 5 entries

    summary_lines = [
        "📊 **Session Summary**",
        "=" * 30,
        f"🎤 Total Analyses: {stats.get('total_processed', 0)}",
        f"✅ Successful: {stats.get('successful_analyses', 0)}",
        f"❌ Failed: {stats.get('failed_analyses', 0)}",
        f"📈 Success Rate: {stats.get('success_rate', 0):.1f}%",
        f"⏱️ Average Time: {stats.get('average_processing_time', 0):.1f}s",
        f"🕒 Session Duration: {stats.get('session_duration', 0):.1f} minutes",
        ""
    ]

    if history:
        summary_lines.extend([
            "📋 **Recent Activity**",
            "-" * 20
        ])

        for entry in history[-3:]:  # Last 3 entries
            timestamp = entry.get('timestamp', '')
            if timestamp:
                # Format timestamp to be more readable
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime("%H:%M")
                except:
                    time_str = timestamp[:5]  # Fallback

                status = "✅" if 'error' not in entry.get('results', {}) else "❌"
                settings = entry.get('settings', {})
                depth = settings.get('analysis_depth', 'Unknown')

                summary_lines.append(f"{status} {time_str} - {depth} analysis")

    return "\n".join(summary_lines)

def reset_session():
    """Reset the entire session state"""

    if hasattr(gr, '_pitch_perfect_session'):
        del gr._pitch_perfect_session

    # Reinitialize
    initialize_session_state()

    return "Session reset successfully"

# Utility functions for hash generation (for caching)
def generate_audio_hash(audio_file_path: str) -> str:
    """Generate a hash for audio file for caching purposes"""

    import hashlib
    import os

    if not audio_file_path or not os.path.exists(audio_file_path):
        return "no_file"

    # Use file size and modification time for quick hash
    stat = os.stat(audio_file_path)
    content = f"{audio_file_path}_{stat.st_size}_{stat.st_mtime}"

    return hashlib.md5(content.encode()).hexdigest()

def generate_settings_hash(settings: Dict) -> str:
    """Generate a hash for settings dictionary"""

    import hashlib

    # Sort settings for consistent hashing
    settings_str = json.dumps(settings, sort_keys=True)
    return hashlib.md5(settings_str.encode()).hexdigest()

# Session state monitoring
def get_session_health() -> Dict:
    """Get health information about the session state"""

    session = gr._pitch_perfect_session

    health = {
        'status': 'healthy',
        'memory_usage': {
            'history_entries': len(session.get('processing_history', [])),
            'cache_entries': len(session.get('analysis_cache', {})),
            'total_objects': len(session)
        },
        'warnings': []
    }

    # Check for potential issues
    if health['memory_usage']['history_entries'] > 100:
        health['warnings'].append("Large processing history - consider clearing")

    if health['memory_usage']['cache_entries'] > 150:
        health['warnings'].append("Large analysis cache - automatic cleanup recommended")

    if len(health['warnings']) > 0:
        health['status'] = 'warning'

    return health
