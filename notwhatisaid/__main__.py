"""
Main entry point for the YouTube Whisper Sync application.
"""

import os
import sys
import subprocess

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
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create upload directory if it doesn't exist
    uploads_dir = os.path.join(base_dir, 'static', 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)

def main():
    """Run the application."""
    if not check_ffmpeg():
        sys.exit(1)
        
    ensure_directories()
    
    # Import here to avoid loading the app before directories are created
    from youtube_whisper_sync.app import app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()