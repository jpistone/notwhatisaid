"""
Benchmarking module for the YouTube Whisper Sync application.
Tracks and records performance metrics for whisper.transcribe.
"""

import time
import json
import os
import psutil
import threading
from datetime import datetime
from pathlib import Path
import functools

# For GPU monitoring
try:
    import pynvml
    has_gpu = True
except ImportError:
    has_gpu = False
    print("pynvml not installed. GPU monitoring will be disabled.")
    print("To enable GPU monitoring, install pynvml: pip install nvidia-ml-py3")

class WhisperBenchmark:
    def __init__(self, output_dir=None):
        """
        Initialize the benchmarking utility.
        
        Args:
            output_dir: Directory to save benchmark results. If None, uses current directory.
        """
        if output_dir is None:
            self.output_dir = Path.cwd() / "benchmarks"
        else:
            self.output_dir = Path(output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize GPU monitoring if available
        if has_gpu:
            try:
                pynvml.nvmlInit()
                self.gpu_count = pynvml.nvmlDeviceGetCount()
            except Exception as e:
                print(f"Failed to initialize GPU monitoring: {e}")
                self.gpu_count = 0
        else:
            self.gpu_count = 0
    
    def get_cpu_usage(self):
        """Get CPU usage as a percentage."""
        return psutil.cpu_percent(interval=0.1)
    
    def get_gpu_usage(self):
        """Get GPU usage information."""
        if not has_gpu or self.gpu_count == 0:
            return None
        
        gpu_info = []
        try:
            for i in range(self.gpu_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                
                gpu_info.append({
                    "index": i,
                    "gpu_util": util.gpu,  # GPU utilization percentage
                    "memory_util": util.memory,  # Memory utilization percentage
                    "memory_used": mem_info.used,
                    "memory_total": mem_info.total
                })
            return gpu_info
        except Exception as e:
            print(f"Error getting GPU usage: {e}")
            return None

    def _monitor_resources(self, stop_event, metrics):
        """Monitor CPU and GPU usage in a separate thread."""
        while not stop_event.is_set():
            cpu_usage = self.get_cpu_usage()
            gpu_usage = self.get_gpu_usage()
            
            metrics["cpu_usage"].append(cpu_usage)
            metrics["gpu_usage"].append(gpu_usage)
            
            time.sleep(0.5)  # Sample every 500ms
    
    def benchmark(self, func=None, **kwargs):
        """
        Decorator to benchmark a function.
        
        Can be used as:
        @benchmark_instance.benchmark
        def function_to_benchmark():
            pass
        
        Or directly:
        result = benchmark_instance.benchmark(whisper.transcribe)(audio_file)
        """
        if func is None:
            return functools.partial(self.benchmark, **kwargs)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function name or override
            func_name = kwargs.pop('benchmark_name', func.__name__)
            
            # Initialize metrics
            metrics = {
                "function": func_name,
                "timestamp": datetime.now().isoformat(),
                "cpu_usage": [],
                "gpu_usage": []
            }
            
            # Set up monitoring thread
            stop_event = threading.Event()
            monitor_thread = threading.Thread(
                target=self._monitor_resources,
                args=(stop_event, metrics)
            )
            
            # Start monitoring
            monitor_thread.start()
            
            # Start timing
            start_time = time.time()
            
            try:
                # Run the function
                result = func(*args, **kwargs)
                
                # End timing
                end_time = time.time()
                
                # Stop monitoring
                stop_event.set()
                monitor_thread.join()
                
                # Calculate final metrics
                execution_time = end_time - start_time
                metrics["execution_time"] = execution_time
                metrics["cpu_usage_avg"] = sum(metrics["cpu_usage"]) / len(metrics["cpu_usage"]) if metrics["cpu_usage"] else 0
                metrics["cpu_usage_max"] = max(metrics["cpu_usage"]) if metrics["cpu_usage"] else 0
                
                # Process GPU metrics if available
                if metrics["gpu_usage"] and any(metrics["gpu_usage"]):
                    # Filter out None values
                    gpu_readings = [g for g in metrics["gpu_usage"] if g]
                    
                    if gpu_readings:
                        # Calculate averages for each GPU
                        gpu_avgs = {}
                        for i in range(self.gpu_count):
                            gpu_utils = [reading[i]["gpu_util"] for reading in gpu_readings if i < len(reading)]
                            mem_utils = [reading[i]["memory_util"] for reading in gpu_readings if i < len(reading)]
                            
                            if gpu_utils and mem_utils:
                                gpu_avgs[f"gpu_{i}"] = {
                                    "gpu_util_avg": sum(gpu_utils) / len(gpu_utils),
                                    "gpu_util_max": max(gpu_utils),
                                    "memory_util_avg": sum(mem_utils) / len(mem_utils),
                                    "memory_util_max": max(mem_utils)
                                }
                        
                        metrics["gpu_usage_summary"] = gpu_avgs
                
                # Save benchmark results
                self.save_results(metrics)
                
                return result
            except Exception as e:
                # End timing even if there's an error
                end_time = time.time()
                execution_time = end_time - start_time
                
                # Stop monitoring
                stop_event.set()
                if monitor_thread.is_alive():
                    monitor_thread.join()
                
                # Add error information to metrics
                metrics["execution_time"] = execution_time
                metrics["error"] = str(e)
                
                # Save benchmark results
                self.save_results(metrics)
                
                # Re-raise the exception
                raise
        
        return wrapper
    
    def save_results(self, metrics):
        """Save benchmark results to a JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"whisper_benchmark_{timestamp}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        print(f"Benchmark results saved to: {filepath}")
        
        # Also save to a consolidated file
        consolidated_file = self.output_dir / "whisper_benchmarks.json"
        
        if consolidated_file.exists():
            with open(consolidated_file, 'r') as f:
                try:
                    all_metrics = json.load(f)
                except json.JSONDecodeError:
                    all_metrics = []
        else:
            all_metrics = []
        
        all_metrics.append(metrics)
        
        with open(consolidated_file, 'w') as f:
            json.dump(all_metrics, f, indent=2)