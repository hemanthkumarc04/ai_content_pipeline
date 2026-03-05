#!/usr/bin/env bash
set -o errexit

# Install ffmpeg (required by MoviePy for video rendering)
apt-get update && apt-get install -y ffmpeg

pip install -r requirements.txt
python manage.py collectstatic --noinput
