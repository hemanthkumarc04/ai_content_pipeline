#!/usr/bin/env bash
<<<<<<< HEAD
set -o errexit

echo "Installing ffmpeg..."
apt-get update && apt-get install -y ffmpeg

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build complete!"
=======
# exit on error
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
>>>>>>> b83beb74479bf6366cd0ff19a82b843db28e52ba
