from setuptools import setup, find_packages

setup(
    name="yt_whisper_sync",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask",
        "pytube",
        "whisper-timestamped",
        "psutil",  # For CPU and memory monitoring
        "py3nvml",  # For NVIDIA GPU monitoring
    ],
    entry_points={
        "console_scripts": [
            "yt-whisper-sync=yt_whisper_sync.__main__:main",
        ],
    },
    python_requires=">=3.7",
)