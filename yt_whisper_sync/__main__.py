"""
Main entry point for the YouTube Whisper Sync application.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_ffmpeg():
    """Check if FFmpeg is installed."""
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✓ FFmpeg is installed")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("✗ FFmpeg is not installed")
        print("Please install FFmpeg before running this application:")
        print("- Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("- MacOS: brew install ffmpeg")
        print("- Windows: Download from https://www.ffmpeg.org/download.html")
        return False

def ensure_directories():
    """Ensure required directories exist."""
    # Get the directory of the current file
    base_dir = Path(__file__).parent
    
    # Create upload directory if it doesn't exist
    uploads_dir = base_dir / 'static' / 'uploads'
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    # Create templates directory if it doesn't exist
    templates_dir = base_dir / 'templates'
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Base directory: {base_dir}")
    print(f"Templates directory: {templates_dir}")
    print(f"Uploads directory: {uploads_dir}")

def main():
    """Run the application."""
    if not check_ffmpeg():
        sys.exit(1)
        
    ensure_directories()
    
    # Import here to avoid loading the app before directories are created
    from yt_whisper_sync.app import app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()