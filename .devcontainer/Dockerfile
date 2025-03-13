FROM mcr.microsoft.com/devcontainers/universal

# Install pydf
RUN apt-get update && apt-get install -y pydf ripgrep

# Copy bashrc
COPY devcontainer_bashrc /home/codespace/.bashrc

# Install 
# USER codespace
# RUN npm install -g @anthropic-ai/claude-code

