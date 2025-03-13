"""
Example of how to integrate the benchmarking with Whisper transcription.
This is a sample implementation that you can adapt to your specific application.
"""

import whisper_timestamped as whisper
from pathlib import Path
from yt_whisper_sync.benchmark import WhisperBenchmark

class TranscriptionService:
    def __init__(self, model_name="base"):
        """
        Initialize the transcription service.
        
        Args:
            model_name: Whisper model name (tiny, base, small, medium, large)
        """
        self.model_name = model_name
        self.model = whisper.load_model(model_name)
        
        # Initialize benchmarking
        current_dir = Path(__file__).parent.parent
        benchmark_dir = current_dir / "benchmarks"
        self.benchmark = WhisperBenchmark(output_dir=benchmark_dir)
    
    def transcribe(self, audio_path):
        """
        Transcribe audio file using Whisper with benchmarking.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            dict: Transcription results
        """
        # Apply benchmarking decorator to the transcribe function
        transcribe_with_benchmark = self.benchmark.benchmark(self.model.transcribe)
        
        # Run transcription with benchmarking
        result = transcribe_with_benchmark(
            audio_path, 
            benchmark_name=f"whisper.transcribe.{self.model_name}"
        )
        
        return result

# Usage example:
# service = TranscriptionService(model_name="base")
# result = service.transcribe("path/to/audio.mp3")