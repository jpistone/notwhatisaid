"""
Entry point script to run the YouTube Whisper Sync application.
"""

from pathlib import Path
import sys

# Add the parent directory to sys.path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# Import from the module
from yt_whisper_sync.app import app

if __name__ == "__main__":
    # Ensure upload folder exists
    upload_folder = current_dir / "yt_whisper_sync" / "static" / "uploads"
    upload_folder.mkdir(parents=True, exist_ok=True)
    
    print(f"Starting YouTube Whisper Sync application...")
    print(f"Project root: {current_dir}")
    print(f"Upload folder: {upload_folder}")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)