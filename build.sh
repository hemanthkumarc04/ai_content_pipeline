#!/usr/bin/env bash
set -o errexit

echo "Installing ffmpeg..."
apt-get update && apt-get install -y ffmpeg

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build complete!"
