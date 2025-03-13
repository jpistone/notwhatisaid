"""
Flask application for YouTube Whisper Sync.
"""

import json
import uuid
from pathlib import Path
from flask import Flask, request, render_template, jsonify, url_for
from pytube import YouTube
import whisper_timestamped

# Get the directory of the current file
# Correctly handle the path for /workspaces/notwhatisaid/yt_whisper_sync/app.py
BASE_DIR = Path(__file__).parent  # Points to /workspaces/notwhatisaid/yt_whisper_sync/
PROJECT_ROOT = BASE_DIR.parent    # Points to /workspaces/notwhatisaid/
UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads'

# Create Flask app
# Make sure template and static folders are absolute paths
template_dir = BASE_DIR / 'templates'
static_dir = BASE_DIR / 'static'

# Create directories if they don't exist
template_dir.mkdir(parents=True, exist_ok=True)
static_dir.mkdir(parents=True, exist_ok=True)

print(f"Template directory: {template_dir}")
print(f"Static directory: {static_dir}")

app = Flask(__name__, 
           template_folder=str(template_dir),
           static_folder=str(static_dir))

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_video():
    """Process a YouTube video URL to extract transcript."""
    youtube_url = request.form.get('youtube_url')
    if not youtube_url:
        return jsonify({'error': 'No YouTube URL provided'}), 400
    
    try:
        # Generate a unique ID for this video processing
        processing_id = str(uuid.uuid4())
        processing_dir = UPLOAD_FOLDER / processing_id
        processing_dir.mkdir(parents=True, exist_ok=True)
        
        # Download YouTube video
        yt = YouTube(youtube_url)
        video_title = yt.title
        
        # Get video stream
        video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        video_path = video_stream.download(output_path=str(processing_dir), filename='video.mp4')
        video_rel_path = Path('uploads') / processing_id / 'video.mp4'
        
        # Extract audio for whisper-timestamped
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_path = audio_stream.download(output_path=str(processing_dir), filename='audio.mp4')
        
        # Generate transcript with whisper-timestamped
        # Note: Using the base model for speed, you can use 'small', 'medium', etc. for better accuracy
        result = whisper_timestamped.transcribe(
            model_size="base", 
            language="en",  # Change as needed or set to None for auto-detection
            audio=audio_path,
            vad=True,  # Voice activity detection for better timestamps
            word_timestamps=True  # Ensure we get word-level timestamps
        )
        
        # Save transcript to JSON file
        transcript_path = processing_dir / 'transcript.json'
        with open(transcript_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        return jsonify({
            'success': True,
            'video_id': processing_id,
            'video_path': str(video_rel_path),
            'video_title': video_title,
            'message': 'Video processed successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/transcript/<video_id>')
def get_transcript(video_id):
    """Get the transcript for a processed video."""
    transcript_path = UPLOAD_FOLDER / video_id / 'transcript.json'
    if not transcript_path.exists():
        return jsonify({'error': 'Transcript not found'}), 404
    
    with open(transcript_path, 'r') as f:
        transcript_data = json.load(f)
    
    return jsonify(transcript_data)

if __name__ == '__main__':
    # Ensure upload folder exists
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)