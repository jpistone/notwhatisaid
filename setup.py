#!/usr/bin/env python3
import os
import subprocess
import sys

def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✓ FFmpeg is installed")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("✗ FFmpeg is not installed")
        return False

def install_ffmpeg():
    if sys.platform.startswith('linux'):
        print("Installing FFmpeg using apt...")
        subprocess.run(['sudo', 'apt-get', 'update'], check=True)
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'ffmpeg'], check=True)
    elif sys.platform == 'darwin':
        print("Installing FFmpeg using Homebrew...")
        try:
            subprocess.run(['brew', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except (subprocess.SubprocessError, FileNotFoundError):
            print("Homebrew not found. Please install Homebrew first: https://brew.sh/")
            sys.exit(1)
        subprocess.run(['brew', 'install', 'ffmpeg'], check=True)
    else:
        print("Please install FFmpeg manually: https://www.ffmpeg.org/download.html")
        sys.exit(1)

def setup_venv():
    if not os.path.exists('venv'):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        
    # Activate virtual environment
    if sys.platform.startswith('win'):
        activate_script = os.path.join('venv', 'Scripts', 'activate')
    else:
        activate_script = os.path.join('venv', 'bin', 'activate')
    
    print(f"To activate the virtual environment, run: source {activate_script}")
    
    # Install requirements
    print("Installing Python dependencies...")
    pip_cmd = [os.path.join('venv', 'Scripts', 'pip') if sys.platform.startswith('win') else os.path.join('venv', 'bin', 'pip')]
    subprocess.run(pip_cmd + ['install', '-r', 'requirements.txt'], check=True)

def create_directories():
    dirs = ['static/uploads', 'templates', 'static/js', 'static/css']
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    print("✓ Created necessary directories")

def main():
    print("Setting up YouTube Transcript Sync...")
    
    if not check_ffmpeg():
        try:
            install_ffmpeg()
        except Exception as e:
            print(f"Error installing FFmpeg: {e}")
            print("Please install FFmpeg manually: https://www.ffmpeg.org/download.html")
    
    create_directories()
    setup_venv()
    
    print("\nSetup complete! To run the application:")
    print("1. Activate the virtual environment")
    print("2. Run: python app.py")
    print("3. Open http://127.0.0.1:5000/ in your browser")

if __name__ == '__main__':
    main()