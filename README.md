# YouTube Transcript Sync

This application takes a YouTube video URL, downloads the video, generates a word-level timestamped transcript using whisper-timestamped, and displays the video alongside the transcript. As the video plays, the transcript scrolls automatically and highlights the word being spoken in real-time.

## Features

- Download YouTube videos via URL
- Generate accurate word-level timestamped transcripts using OpenAI's Whisper model
- Synchronized highlighting of words as they are spoken in the video
- Interactive transcript - click any word to jump to that position in the video
- Responsive design that works on desktop and mobile

## Prerequisites

- Python 3.8 or higher
- FFmpeg (required for audio processing)

## Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/youtube-whisper-sync
cd youtube-whisper-sync
```

2. Create a virtual environment and activate it:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```
pip install whisper-timestamped pytube flask
```

4. Install FFmpeg (if not already installed):
   - **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
   - **MacOS**: `brew install ffmpeg`
   - **Windows**: Download from [FFmpeg official site](https://www.ffmpeg.org/download.html) or use `choco install ffmpeg` with Chocolatey

## Usage

1. Start the Flask server:
```
python app.py
```

2. Open your browser and navigate to `http://127.0.0.1:5000/`

3. Enter a YouTube URL and click "Process Video"

4. Wait for the processing to complete (this may take several minutes depending on the video length)

5. Once processed, the video will appear with its transcript beneath it

6. Play the video and observe how the words in the transcript are highlighted as they're spoken

7. Click on any word in the transcript to jump to that point in the video

## How It Works

1. The application uses pytube to download the YouTube video and its audio
2. The audio is processed by whisper-timestamped to generate word-level timestamps
3. The Flask backend serves the video and transcript data
4. JavaScript code synchronizes the video playback with the transcript, highlighting words in real-time

## Notes

- Processing time depends on video length, your computer's processing power, and the Whisper model size
- The default configuration uses the "base" model for speed; you can change to "small", "medium", or "large" for better accuracy but slower processing
- The application stores downloaded videos and transcripts in the `static/uploads` directory

## Limitations

- YouTube URLs with age restrictions or other access limitations may not work
- Very long videos may take a long time to process
- Transcript accuracy depends on audio quality and the Whisper model used

## License

This project is licensed under the MIT License - see the LICENSE file for details.