#!/usr/bin/env bash

# Install Chrome
mkdir -p /opt/render/project/.render/chrome
cd /opt/render/project/.render/chrome
curl -O https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get update && apt-get install -y ./google-chrome-stable_current_amd64.deb

# Move back to project root
cd /opt/render/project/src

# Install Python dependencies
pip install -r requirements.txt
