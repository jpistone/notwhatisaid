import os
import json
import uuid
from flask import Flask, request, render_template, jsonify
from pytube import YouTube
import whisper_timestamped

app = Flask(__name__)

# Directory to store downloaded videos and transcripts
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_video():
    youtube_url = request.form.get('youtube_url')
    if not youtube_url:
        return jsonify({'error': 'No YouTube URL provided'}), 400
    
    try:
        # Generate a unique ID for this video processing
        processing_id = str(uuid.uuid4())
        processing_dir = os.path.join(UPLOAD_FOLDER, processing_id)
        os.makedirs(processing_dir, exist_ok=True)
        
        # Download YouTube video
        yt = YouTube(youtube_url)
        video_title = yt.title
        
        # Get video stream
        video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        video_path = video_stream.download(output_path=processing_dir, filename='video.mp4')
        video_rel_path = os.path.join('uploads', processing_id, 'video.mp4')
        
        # Extract audio for whisper-timestamped
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_path = audio_stream.download(output_path=processing_dir, filename='audio.mp4')
        
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
        transcript_path = os.path.join(processing_dir, 'transcript.json')
        with open(transcript_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        return jsonify({
            'success': True,
            'video_id': processing_id,
            'video_path': video_rel_path,
            'video_title': video_title,
            'message': 'Video processed successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/transcript/<video_id>')
def get_transcript(video_id):
    transcript_path = os.path.join(UPLOAD_FOLDER, video_id, 'transcript.json')
    if not os.path.exists(transcript_path):
        return jsonify({'error': 'Transcript not found'}), 404
    
    with open(transcript_path, 'r') as f:
        transcript_data = json.load(f)
    
    return jsonify(transcript_data)

if __name__ == '__main__':
    app.run(debug=True)