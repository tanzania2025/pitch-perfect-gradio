#!/usr/bin/env python3
"""
Script to create all missing __init__.py files and any other required files
for the Pitch Perfect Gradio frontend
"""

import os

def create_init_files():
    """Create __init__.py files for all packages"""

    # Define packages that need __init__.py files
    packages = [
        'components',
        'utils'
    ]

    for package in packages:
        init_file_path = os.path.join(package, '__init__.py')

        if not os.path.exists(init_file_path):
            os.makedirs(package, exist_ok=True)

            with open(init_file_path, 'w') as f:
                f.write(f'"""\n{package.title()} package for Pitch Perfect Gradio frontend\n"""\n\n')

                # Add package-specific imports if needed
                if package == 'components':
                    f.write("""from .audio_input import create_audio_input
from .results_display import create_results_display, format_analysis_results
from .settings_panel import create_settings_panel

__all__ = [
    'create_audio_input',
    'create_results_display',
    'format_analysis_results',
    'create_settings_panel'
]
""")
                elif package == 'utils':
                    f.write("""from .session_state import initialize_session_state
from .audio_utils import validate_audio_file

__all__ = [
    'initialize_session_state',
    'validate_audio_file'
]
""")

            print(f"✅ Created {init_file_path}")
        else:
            print(f"📁 {init_file_path} already exists")

def create_directories():
    """Create required directories"""

    directories = [
        'components',
        'utils',
        'static',
        'static/css',
        'static/images',
        'outputs',
        'temp'
    ]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"📁 Created directory: {directory}")
        else:
            print(f"📁 Directory exists: {directory}")

def create_sample_files():
    """Create sample audio files directory structure"""

    samples_dir = 'static/samples'
    if not os.path.exists(samples_dir):
        os.makedirs(samples_dir, exist_ok=True)

        # Create placeholder files
        sample_files = [
            'business_presentation.wav',
            'casual_conversation.wav',
            'public_speaking.wav',
            'interview_response.wav'
        ]

        for sample_file in sample_files:
            sample_path = os.path.join(samples_dir, sample_file)
            if not os.path.exists(sample_path):
                # Create placeholder file (in real implementation, these would be actual audio files)
                with open(sample_path, 'w') as f:
                    f.write(f"# Placeholder for {sample_file}\n")
                print(f"📄 Created placeholder: {sample_path}")

def check_required_files():
    """Check if all required files exist"""

    required_files = [
        'app.py',
        'config.py',
        'api_client.py',
        'requirements.txt',
        'components/audio_input.py',
        'components/results_display.py',
        'components/settings_panel.py',
        'utils/session_state.py',
        'utils/audio_utils.py',
        'static/css/custom.css'
    ]

    missing_files = []

    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        print("\n❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print("\n✅ All required files are present!")
        return True

def main():
    """Main setup function"""

    print("🚀 Setting up Pitch Perfect Gradio Frontend...")
    print("=" * 50)

    # Create directories
    print("\n📁 Creating directories...")
    create_directories()

    # Create __init__.py files
    print("\n📄 Creating __init__.py files...")
    create_init_files()

    # Create sample files
    print("\n🎵 Creating sample files structure...")
    create_sample_files()

    # Check for missing files
    print("\n🔍 Checking for required files...")
    all_files_present = check_required_files()

    print("\n" + "=" * 50)

    if all_files_present:
        print("🎉 Setup complete! You should now be able to run:")
        print("   python app.py")
        print("\n💡 Next steps:")
        print("   1. Make sure your backend API is running")
        print("   2. Update config.py with your backend URL")
        print("   3. Test the application")
    else:
        print("⚠️  Some files are missing. Please create them before running the app.")

    print("\n📚 Documentation: Check the generated component files for implementation details.")

if __name__ == "__main__":
    main()
