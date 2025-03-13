FROM mcr.microsoft.com/devcontainers/universal

# Install pydf
RUN apt-get update && apt-get install -y pydf ripgrep

# Copy bashrc
COPY devcontainer_bashrc /home/codespace/.bashrc

# Project-specific dependencies
RUN apt-get install ffmpeg

# Install 
# USER codespace
# RUN pip install whisper-timestamped


