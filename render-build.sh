#!/usr/bin/env bash

# Install Chrome
mkdir -p /opt/render/project/.render/chrome
cd /opt/render/project/.render/chrome
curl -O https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get update && apt-get install -y ./google-chrome-stable_current_amd64.deb

# Install Python dependencies
pip install -r requirements.txt
