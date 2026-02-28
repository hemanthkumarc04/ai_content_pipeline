# ai_content_pipeline

# AI-Powered Short-Form Content Automator 🎬🤖

An automated, full-stack web application built with Python and Django that streamlines the creation of short-form video content. It takes a text script and a background video, generates a realistic AI voiceover, and automatically stitches them together into a final, perfectly timed `.mp4` file.

## 🚀 Features
* **Automated Voice Generation:** Integrates with Text-to-Speech (TTS) REST APIs to generate high-quality voiceovers from text scripts.
* **Smart Video Processing:** Automatically trims background footage to match the exact duration of the generated audio.
* **Seamless Media Merging:** Uses Python's `MoviePy` to stitch audio and video tracks together programmatically.
* **Intuitive Web UI:** A clean Django-based frontend where users can easily input scripts and upload media.

## 🛠️ Technology Stack
* **Backend Framework:** Python, Django
* **Video Processing:** `moviepy`
* **API Integration:** `requests` (for TTS API communication)
* **Frontend:** HTML, CSS, Django Templates
* **Version Control & IDE:** Git, GitHub, VS Code

## 📋 Prerequisites
Before you begin, ensure you have the following installed on your machine:
* [Python 3.8+](https://www.python.org/downloads/)
* `pip` (Python package manager)
* [FFmpeg](https://ffmpeg.org/download.html) (Required by MoviePy for video rendering)

## ⚙️ Local Setup & Installation

**1. Clone the repository**
```bash
git clone [https://github.com/your-username/content-automator.git](https://github.com/your-username/content-automator.git)
cd content-automator

# Create and activate a virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
# source venv/bin/activate

#Install dependencies
pip install -r requirements.txt


# Set up the Database (Apply Migrations)
python manage.py makemigrations
python manage.py migrate


# Run the Development Server
python manage.py runserver
Navigate to http://127.0.0.1:8000/ in your browser to view the application.