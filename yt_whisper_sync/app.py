"""
Flask application for YouTube Whisper Sync.
"""

import json
import uuid
import sys
from pathlib import Path
from flask import Flask, request, render_template, jsonify, url_for
from pytubefix import YouTube
import whisper_timestamped as whisper
from yt_whisper_sync.benchmark import WhisperBenchmark

# Get the directory of the current file
# Correctly handle the path for /workspaces/notwhatisaid/yt_whisper_sync/app.py
BASE_DIR = Path(__file__).parent  # Points to /workspaces/notwhatisaid/yt_whisper_sync/
PROJECT_ROOT = BASE_DIR.parent    # Points to /workspaces/notwhatisaid/
# Set up upload folder
UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads'
# Make sure the upload folder exists
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
print(f"Upload folder: {UPLOAD_FOLDER}")
# Initialize benchmark directory (add after UPLOAD_FOLDER.mkdir line)
BENCHMARK_DIR = PROJECT_ROOT / 'benchmarks'
BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)
print(f"Benchmark directory: {BENCHMARK_DIR}")

# Initialize benchmarking
try:
    benchmark = WhisperBenchmark(output_dir=BENCHMARK_DIR)
    print("Whisper benchmarking initialized successfully")
except Exception as e:
    print(f"Warning: Could not initialize benchmarking: {e}")

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

@app.route('/status')
def status():
    """Check if the API is working."""
    static_path = BASE_DIR / 'static'
    template_path = BASE_DIR / 'templates'
    
    return jsonify({
        'status': 'ok',
        'base_dir': str(BASE_DIR),
        'static_dir_exists': static_path.exists(),
        'template_dir_exists': template_path.exists(),
        'upload_dir_exists': UPLOAD_FOLDER.exists(),
        'whisper_available': 'whisper_timestamped' in sys.modules,
        'pytube_available': 'pytubefix' in sys.modules
    })

@app.route('/process', methods=['POST'])
def process_video():
    """Process a YouTube video URL to extract transcript."""
    youtube_url = request.form.get('youtube_url')
    if not youtube_url:
        return jsonify({'error': 'No YouTube URL provided'}), 400
    
    try:
        print(f"Processing video: {youtube_url}")
        
        # Generate a unique ID for this video processing
        processing_id = str(uuid.uuid4())
        processing_dir = UPLOAD_FOLDER / processing_id
        processing_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created processing directory: {processing_dir}")
        
        # Download YouTube video
        print("Initializing YouTube downloader...")
        yt = YouTube(youtube_url)
        
        # Try to get video title safely with a fallback
        try:
            video_title = yt.streams[0].title
        except (KeyError, AttributeError):
            print("Could not get video title from standard property, trying alternative method...")
            try:
                # Alternative way to get title from initial data
                if hasattr(yt, 'initial_data') and yt.initial_data:
                    video_details = yt.initial_data.get('videoDetails', {})
                    video_title = video_details.get('title', 'Unknown Title')
                else:
                    # Extract video ID and use as fallback title
                    import re
                    video_id = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', youtube_url)
                    video_title = f"Video {video_id.group(1) if video_id else 'Unknown'}"
            except Exception as title_error:
                print(f"Error getting title via alternative method: {str(title_error)}")
                video_title = "Unknown Title"
        
        print(f"Video title: {video_title}")
        
        # Get video stream
        print("Getting video stream...")
        video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        if not video_stream:
            print("No suitable video stream found. Trying any available stream...")
            video_stream = yt.streams.filter(file_extension='mp4').first()
            if not video_stream:
                return jsonify({'error': 'No suitable video stream found'}), 400
        
        print(f"Selected video stream: {video_stream}")
        video_path = video_stream.download(output_path=str(processing_dir), filename='video.mp4')
        video_rel_path = Path('uploads') / processing_id / 'video.mp4'
        print(f"Video downloaded to: {video_path}")
        
        # Extract audio for whisper-timestamped
        print("Getting audio stream...")
        audio_stream = yt.streams.filter(only_audio=True).first()
        if not audio_stream:
            print("No audio stream found. Using video stream for audio...")
            audio_stream = video_stream
        
        audio_path = audio_stream.download(output_path=str(processing_dir), filename='audio.mp4')
        print(f"Audio downloaded to: {audio_path}")
        
        # Generate transcript with whisper-timestamped
        print("Starting transcription with whisper-timestamped...")
        audio = whisper.load_audio(audio_path)
        # Why does tiny produce the best results?
        model = whisper.load_model("turbo")
        
        transcribe_with_benchmark = benchmark.benchmark(whisper.transcribe)
        result = transcribe_with_benchmark(model, audio, language="en")
        print("Transcription completed successfully")
        
        # Save transcript to JSON file
        transcript_path = processing_dir / 'transcript.json'
        with open(transcript_path, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Transcript saved to: {transcript_path}")
        
        # Log the response being sent
        response_data = {
            'success': True,
            'video_id': processing_id,
            'video_path': str(video_rel_path),
            'video_title': video_title,
            'message': 'Video processed successfully'
        }
        print(f"Sending response: {response_data}")
        
        return jsonify(response_data)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error processing video: {str(e)}")
        print(f"Error details: {error_details}")
        return jsonify({
            'error': str(e),
            'details': error_details
        }), 500

@app.route('/transcript/<video_id>')
def get_transcript(video_id):
    """Get the transcript for a processed video."""
    transcript_path = UPLOAD_FOLDER / video_id / 'transcript.json'
    if not transcript_path.exists():
        return jsonify({'error': 'Transcript not found'}), 404
    
    with open(transcript_path, 'r') as f:
        transcript_data = json.load(f)
    
    return jsonify(transcript_data)

@app.route('/benchmarks')
def view_benchmarks():
    """Display all saved benchmark data."""
    # Path to the consolidated benchmarks file
    consolidated_file = BENCHMARK_DIR / "whisper_benchmarks.json"
    
    if not consolidated_file.exists():
        return render_template('benchmarks.html', 
                              benchmarks=None, 
                              error="No benchmark data found. Run some transcriptions first.")
    
    try:
        with open(consolidated_file, 'r') as f:
            benchmarks = json.load(f)
            
        # Sort benchmarks by timestamp (newest first)
        benchmarks.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return render_template('benchmarks.html', 
                              benchmarks=benchmarks, 
                              error=None)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return render_template('benchmarks.html', 
                              benchmarks=None, 
                              error=f"Error loading benchmark data: {str(e)}")

if __name__ == '__main__':
    # Ensure upload folder exists
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)