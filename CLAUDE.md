# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pitch Perfect is an AI-powered speech improvement system built with Gradio that analyzes audio files and provides comprehensive speech coaching through sentiment analysis, tonal features, and AI-generated improvements.

## Essential Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the full application (requires backend)
python app.py

# Run minimal UI version (no backend required, for UI development)
python app_minimal.py
```

### Testing and Validation
```bash
# No test command found - add tests in tests/ directory
# Audio validation can be tested via utils/audio_utils.py
```

## Architecture

### Client-Server Architecture
- **Frontend**: Gradio application (this repository)
- **Backend API**: https://pitch-perfect-backend-792590041292.europe-west1.run.app/
  - Endpoints: `/health`, `/process-audio`
  - Handles audio processing and AI analysis

### Key Components
1. **api_client.py**: Backend communication layer
   - Handles audio uploads and API responses
   - Error handling and retry logic

2. **components/results_display.py**: Rich results UI
   - 6 tabs: Transcript, Sentiment, Tonal, Improvements, Audio, Charts
   - Uses Plotly for visualizations

3. **components/settings_panel.py**: Configuration interface
   - Voice selection, analysis depth, improvement focus
   - Processing presets

4. **utils/audio_utils.py**: Audio validation
   - Format checking (wav, mp3, m4a, flac)
   - Size/duration limits (25MB, 5 minutes)

### Configuration Management
- **config.py**: Central configuration
  - Backend URL from environment
  - Audio processing limits
  - Gradio server settings
- **.env**: Environment variables (copy from .env.example)


## Development Guidelines

### When modifying the UI:
1. Use `app_minimal.py` for faster iteration without backend
2. Components are in `components/` directory
3. Gradio 4.0+ patterns for state management

### When working with audio:
1. Check audio_utils.py for validation logic
2. Respect limits: 25MB max size, 5 min duration
3. Supported formats: wav, mp3, m4a, flac

### When updating API integration:
1. Backend endpoints are in api_client.py
2. API base URL is configured via BACKEND_URL env var
3. Handle errors gracefully with user-friendly messages


## Error Handling Guidelines

When errors are shown or fixes are needed:
1. Make fixes directly in the code
2. Write as few new lines as possible
3. Prefer modifying existing code over creating new files

## Feature Design Guidelines

When designing new features or modules:
1. Start with the simplest architecture that works
2. Present the basic implementation first
3. Ask if the user wants options for more complex/comprehensive versions
4. Only add complexity when explicitly requested