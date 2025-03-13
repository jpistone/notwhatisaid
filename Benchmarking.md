# Whisper Benchmarking Implementation Guide

## Overview

This guide explains how to implement the Whisper transcription benchmarking in your YouTube Whisper Sync application. The benchmarking functionality tracks:

- Execution time of the `whisper.transcribe` function
- CPU usage during transcription
- GPU usage (if available) during transcription

All metrics are saved in JSON format for easy analysis.

## Setup Instructions

1. **Install dependencies**:
   ```bash
   pip install psutil
   pip install nvidia-ml-py3  # For GPU monitoring
   ```

2. **Add the benchmark module** to your project structure:
   - Copy the `benchmark.py` file to your `yt_whisper_sync` directory

3. **Update your application code** to use benchmarking:

### Option 1: Modify your existing transcription function

Find the module where you call `whisper.transcribe` and modify it like this:

```python
from yt_whisper_sync.benchmark import WhisperBenchmark

# Initialize benchmark
benchmark = WhisperBenchmark(output_dir="path/to/benchmarks")

# Original code:
# result = model.transcribe(audio_file)

# Modified code with benchmarking:
transcribe_with_benchmark = benchmark.benchmark(model.transcribe)
result = transcribe_with_benchmark(audio_file, benchmark_name="whisper.transcribe")
```

### Option 2: Create a wrapper service class

Create a TranscriptionService class as shown in the provided example and use it in your application.

## Benchmark Results

Benchmark results are saved in two formats:

1. **Individual benchmark files**: Each transcription run generates a JSON file with timestamp in the filename
2. **Consolidated file**: All benchmark results are also appended to `whisper_benchmarks.json`

## JSON Format

The benchmark JSON includes:

```json
{
  "function": "whisper.transcribe.base",
  "timestamp": "2023-01-01T12:34:56.789",
  "execution_time": 15.2,
  "cpu_usage": [10.5, 45.2, 60.1, ...],
  "gpu_usage": [...],
  "cpu_usage_avg": 45.6,
  "cpu_usage_max": 75.3,
  "gpu_usage_summary": {
    "gpu_0": {
      "gpu_util_avg": 65.4,
      "gpu_util_max": 95.2,
      "memory_util_avg": 30.5,
      "memory_util_max": 45.6
    }
  }
}
```

## Visualization and Analysis

You can create scripts to visualize the benchmark data or add a section to your app UI to display performance metrics. Consider adding:

- A time series chart of CPU/GPU usage
- Comparison of different model sizes
- Performance over time for repeated transcriptions

## Troubleshooting

- **GPU monitoring not working**: Make sure you have NVIDIA drivers and CUDA properly installed
- **Missing data**: Check that the benchmark directory is writable by the application
- **Performance impact**: If the monitoring itself impacts performance, increase the sampling interval in the `_monitor_resources` method