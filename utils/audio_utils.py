"""
Audio utility functions for the Pitch Perfect Gradio application
"""

import os
import wave
import tempfile
import hashlib
from typing import Dict, Any, Optional, Tuple
from config import Config

def validate_audio_file(audio_file_path: str) -> Dict[str, Any]:
    """
    Comprehensive audio file validation

    Returns:
        Dict with 'valid', 'message', and 'info' keys
    """

    if not audio_file_path:
        return {
            'valid': False,
            'message': "No audio file provided",
            'info': {}
        }

    if not os.path.exists(audio_file_path):
        return {
            'valid': False,
            'message': "Audio file not found",
            'info': {}
        }

    try:
        # Basic file information
        file_info = get_file_info(audio_file_path)

        # Check file size
        if file_info['size_mb'] > Config.MAX_UPLOAD_SIZE:
            return {
                'valid': False,
                'message': f"File too large: {file_info['size_mb']:.1f}MB (max: {Config.MAX_UPLOAD_SIZE}MB)",
                'info': file_info
            }

        # Check file extension
        file_ext = os.path.splitext(audio_file_path)[1].lower()
        supported_exts = [f".{fmt.lower()}" for fmt in Config.SUPPORTED_FORMATS]

        if file_ext not in supported_exts:
            return {
                'valid': False,
                'message': f"Unsupported format: {file_ext}. Supported: {', '.join(supported_exts)}",
                'info': file_info
            }

        # Try to get audio-specific information
        audio_info = get_audio_info(audio_file_path)
        file_info.update(audio_info)

        # Check duration if available
        if 'duration' in audio_info and audio_info['duration'] > Config.MAX_AUDIO_DURATION:
            return {
                'valid': False,
                'message': f"Audio too long: {audio_info['duration']:.1f}s (max: {Config.MAX_AUDIO_DURATION}s)",
                'info': file_info
            }

        return {
            'valid': True,
            'message': f"Audio file validated successfully ({file_info['size_mb']:.1f}MB)",
            'info': file_info
        }

    except Exception as e:
        return {
            'valid': False,
            'message': f"Validation error: {str(e)}",
            'info': {}
        }

def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get basic file information"""

    try:
        stat = os.stat(file_path)

        return {
            'filename': os.path.basename(file_path),
            'size_bytes': stat.st_size,
            'size_mb': stat.st_size / (1024 * 1024),
            'format': os.path.splitext(file_path)[1].upper(),
            'modified': stat.st_mtime,
            'path': file_path
        }
    except Exception as e:
        return {'error': str(e)}

def get_audio_info(audio_file_path: str) -> Dict[str, Any]:
    """Extract detailed audio information from file"""

    audio_info = {}

    try:
        # Handle WAV files with wave module
        if audio_file_path.lower().endswith('.wav'):
            audio_info.update(get_wav_info(audio_file_path))

        # For other formats, try with librosa if available
        else:
            audio_info.update(get_librosa_info(audio_file_path))

    except Exception as e:
        audio_info['error'] = f"Could not read audio info: {str(e)}"

    return audio_info

def get_wav_info(wav_file_path: str) -> Dict[str, Any]:
    """Get information from WAV file using wave module"""

    try:
        with wave.open(wav_file_path, 'rb') as wav_file:
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()

            duration = frames / sample_rate if sample_rate > 0 else 0

            return {
                'duration': duration,
                'sample_rate': sample_rate,
                'channels': channels,
                'sample_width': sample_width,
                'frames': frames,
                'format_detail': f"{sample_rate}Hz, {channels}ch, {sample_width*8}bit"
            }

    except Exception as e:
        return {'wav_error': str(e)}

def get_librosa_info(audio_file_path: str) -> Dict[str, Any]:
    """Get audio information using librosa (if available)"""

    try:
        import librosa

        # Load audio file
        y, sr = librosa.load(audio_file_path, sr=None)

        duration = len(y) / sr

        # Basic audio analysis
        rms_energy = float(librosa.feature.rms(y=y).mean())
        spectral_centroid = float(librosa.feature.spectral_centroid(y=y, sr=sr).mean())

        return {
            'duration': duration,
            'sample_rate': sr,
            'channels': 1,  # librosa loads as mono by default
            'rms_energy': rms_energy,
            'spectral_centroid': spectral_centroid,
            'format_detail': f"{sr}Hz, mono"
        }

    except ImportError:
        return {'librosa_error': 'librosa not available for advanced audio analysis'}
    except Exception as e:
        return {'librosa_error': str(e)}

def create_audio_preview_text(file_info: Dict[str, Any]) -> str:
    """Create formatted text preview of audio file information"""

    if 'error' in file_info:
        return f"❌ Error: {file_info['error']}"

    lines = [
        "📄 **Audio File Information**",
        f"📁 **Filename:** {file_info.get('filename', 'Unknown')}",
        f"📏 **Size:** {file_info.get('size_mb', 0):.2f} MB",
        f"🎵 **Format:** {file_info.get('format', 'Unknown')}"
    ]

    if 'duration' in file_info:
        duration = file_info['duration']
        minutes = int(duration // 60)
        seconds = int(duration % 60)

        if minutes > 0:
            duration_str = f"{minutes}m {seconds}s"
        else:
            duration_str = f"{seconds}s"

        lines.append(f"⏱️ **Duration:** {duration_str}")

    if 'format_detail' in file_info:
        lines.append(f"🔧 **Details:** {file_info['format_detail']}")

    if 'sample_rate' in file_info:
        lines.append(f"📊 **Sample Rate:** {file_info['sample_rate']} Hz")

    if 'channels' in file_info:
        channel_text = "Stereo" if file_info['channels'] == 2 else f"{file_info['channels']} channel(s)"
        lines.append(f"🎧 **Channels:** {channel_text}")

    return "\n".join(lines)

def generate_audio_hash(audio_file_path: str) -> str:
    """Generate a hash for audio file (for caching)"""

    if not audio_file_path or not os.path.exists(audio_file_path):
        return "no_file"

    try:
        # Use file stats for quick hashing
        stat = os.stat(audio_file_path)
        content = f"{audio_file_path}_{stat.st_size}_{stat.st_mtime}"

        return hashlib.md5(content.encode()).hexdigest()[:16]  # Short hash

    except Exception:
        return "hash_error"

def prepare_audio_for_processing(audio_file_path: str, settings: Dict[str, Any]) -> str:
    """
    Prepare audio file for processing based on settings

    Returns path to processed audio file (may be original or temporary processed file)
    """

    if not audio_file_path or not os.path.exists(audio_file_path):
        raise ValueError("Invalid audio file path")

    # Check if any preprocessing is needed
    needs_preprocessing = (
        settings.get('audio_preprocessing', False) or
        settings.get('normalize_volume', False) or
        settings.get('trim_silence', False)
    )

    if not needs_preprocessing:
        return audio_file_path

    try:
        # Create temporary file for processed audio
        temp_file = tempfile.NamedTemporaryFile(
            suffix='.wav',
            delete=False,
            prefix='pp_processed_'
        )
        temp_path = temp_file.name
        temp_file.close()

        # Apply preprocessing (placeholder implementation)
        processed_path = apply_audio_preprocessing(
            audio_file_path,
            temp_path,
            settings
        )

        return processed_path

    except Exception as e:
        # If preprocessing fails, return original file
        print(f"Audio preprocessing failed: {e}")
        return audio_file_path

def apply_audio_preprocessing(input_path: str, output_path: str, settings: Dict[str, Any]) -> str:
    """
    Apply audio preprocessing based on settings

    This is a placeholder implementation. In a real application, you would use
    libraries like librosa, pydub, or scipy for actual audio processing.
    """

    try:
        # For now, just copy the file (placeholder)
        import shutil
        shutil.copy2(input_path, output_path)

        # Here you would implement actual preprocessing:
        # - Noise reduction using noisereduce library
        # - Volume normalization using pydub
        # - Silence trimming using librosa
        # - Audio enhancement filters

        return output_path

    except Exception as e:
        raise Exception(f"Audio preprocessing failed: {e}")

def cleanup_temp_audio_files(file_paths: list):
    """Clean up temporary audio files"""

    for file_path in file_paths:
        try:
            if file_path and os.path.exists(file_path) and 'pp_processed_' in file_path:
                os.remove(file_path)
        except Exception as e:
            print(f"Could not cleanup temp file {file_path}: {e}")

def create_audio_quality_report(audio_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a quality assessment report for the audio file
    """

    quality_report = {
        'overall_score': 'Unknown',
        'issues': [],
        'recommendations': [],
        'technical_quality': 'Unknown'
    }

    try:
        # Sample rate assessment
        sample_rate = audio_info.get('sample_rate', 0)

        if sample_rate < 16000:
            quality_report['issues'].append("Low sample rate may affect analysis quality")
            quality_report['recommendations'].append("Consider using audio with 16kHz+ sample rate")
        elif sample_rate >= 44100:
            quality_report['technical_quality'] = 'High'
        else:
            quality_report['technical_quality'] = 'Good'

        # Duration assessment
        duration = audio_info.get('duration', 0)

        if duration < 5:
            quality_report['issues'].append("Very short audio may limit analysis depth")
            quality_report['recommendations'].append("Try recording 10+ seconds for better results")
        elif duration > 300:
            quality_report['issues'].append("Long audio may take longer to process")
            quality_report['recommendations'].append("Consider splitting into shorter segments")

        # File size assessment
        size_mb = audio_info.get('size_mb', 0)

        if size_mb > 20:
            quality_report['issues'].append("Large file size")
            quality_report['recommendations'].append("Consider compressing audio if upload is slow")

        # Overall score calculation
        issue_count = len(quality_report['issues'])

        if issue_count == 0:
            quality_report['overall_score'] = 'Excellent'
        elif issue_count == 1:
            quality_report['overall_score'] = 'Good'
        elif issue_count == 2:
            quality_report['overall_score'] = 'Fair'
        else:
            quality_report['overall_score'] = 'Needs Improvement'

    except Exception as e:
        quality_report['error'] = str(e)

    return quality_report

def format_audio_quality_report(quality_report: Dict[str, Any]) -> str:
    """Format quality report as readable text"""

    if 'error' in quality_report:
        return f"❌ Quality assessment error: {quality_report['error']}"

    lines = [
        f"🎯 **Audio Quality: {quality_report['overall_score']}**"
    ]

    if quality_report.get('technical_quality') != 'Unknown':
        lines.append(f"🔧 Technical Quality: {quality_report['technical_quality']}")

    issues = quality_report.get('issues', [])
    if issues:
        lines.append("\n⚠️ **Issues Found:**")
        for issue in issues:
            lines.append(f"• {issue}")

    recommendations = quality_report.get('recommendations', [])
    if recommendations:
        lines.append("\n💡 **Recommendations:**")
        for rec in recommendations:
            lines.append(f"• {rec}")

    if not issues and not recommendations:
        lines.append("✅ No issues detected - audio looks good for processing!")

    return "\n".join(lines)

# Audio format conversion utilities (placeholders for future implementation)
def convert_to_wav(input_path: str) -> str:
    """Convert audio file to WAV format (placeholder)"""

    # This would use pydub or similar library for actual conversion
    # For now, assume input is already in supported format
    return input_path

def optimize_for_processing(audio_path: str) -> str:
    """Optimize audio file for speech processing (placeholder)"""

    # This would:
    # - Convert to mono if stereo
    # - Resample to optimal rate (e.g., 16kHz)
    # - Apply basic normalization

    return audio_path
