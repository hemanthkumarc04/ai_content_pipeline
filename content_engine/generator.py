import os
import traceback
import requests
from moviepy import VideoFileClip, AudioFileClip
from dotenv import load_dotenv, find_dotenv, set_key
from gtts import gTTS


def _get_api_key():
    """Load API_KEY from environment variables (supports Render + .env)."""
    # First check os.environ (set via Render Dashboard)
    key = os.environ.get('API_KEY')
    if key:
        return key
    # Fallback: try loading from .env file (local dev)
    env_path = find_dotenv()
    if env_path:
        load_dotenv(env_path)
    else:
        load_dotenv()
    return os.getenv('API_KEY')


def _tts_elevenlabs(script_text, audio_path):
    """Try generating audio with ElevenLabs. Returns True on success."""
    API_KEY = _get_api_key()
    if not API_KEY:
        print("⚠️ API_KEY not found — skipping ElevenLabs.")
        return False

    VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # Adam
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": API_KEY,
    }
    data = {
        "text": script_text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability": 0.35,
            "similarity_boost": 0.8,
            "style": 0.5,
            "use_speaker_boost": True,
        },
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"⚠️ ElevenLabs API Error ({response.status_code}): {response.text}")
            return False

        with open(audio_path, "wb") as f:
            f.write(response.content)
        print("✅ ElevenLabs voiceover downloaded.")
        return True
    except Exception as e:
        print(f"⚠️ ElevenLabs request failed: {e}")
        return False


def _tts_gtts(script_text, audio_path):
    """Fallback: generate audio with Google TTS (gTTS)."""
    try:
        tts = gTTS(text=script_text, lang="en", slow=False)
        tts.save(audio_path)
        print("✅ gTTS voiceover generated (fallback).")
        return True
    except Exception as e:
        print(f"❌ gTTS also failed: {e}")
        return False


def build_video(video_path, script_text):
    print("🎬 Pro AI Engine Started...")

    try:
        # 1. Setup Folders
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        media_folder = os.path.join(base_dir, "media")
        os.makedirs(media_folder, exist_ok=True)

        audio_path = os.path.join(media_folder, "temp_voice.mp3")

        # 2. Generate Voiceover — ElevenLabs first, then gTTS fallback
        print("🗣️ Generating voiceover...")
        if not _tts_elevenlabs(script_text, audio_path):
            print("🔄 Falling back to Google TTS...")
            if not _tts_gtts(script_text, audio_path):
                print("❌ All TTS engines failed. Cannot generate video.")
                return None

        # 3. Mix Video and Audio
        print("✂️ Mixing Video and Audio...")
        video_clip = VideoFileClip(video_path)
        voice_clip = AudioFileClip(audio_path)

        final_video = video_clip.subclipped(0, voice_clip.duration)
        final_video = final_video.with_audio(voice_clip)

        # 4. Export
        output_filename = "final_output.mp4"
        output_path = os.path.join(media_folder, output_filename)

        print("⏳ Rendering Final Video...")
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")

        # Clean up
        voice_clip.close()
        video_clip.close()
        if os.path.exists(audio_path):
            os.remove(audio_path)

        print("✅ Pro AI Engine Finished Successfully!")
        return output_filename

    except Exception as e:
        print(f"❌ Error during processing: {e}")
        traceback.print_exc()
        return None


def set_api_key(new_key, env_file=None):
    """Update or create API_KEY in the project's .env file.

    Args:
        new_key (str): The API key value to write.
        env_file (str, optional): Path to the .env file. If omitted, will try to
            locate one with `find_dotenv()` or create `.env` at the project root.
    Returns:
        bool: True on success, False otherwise.
    """
    try:
        if env_file is None:
            env_file = find_dotenv()
            if not env_file:
                # create .env at project root
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                env_file = os.path.join(project_root, '.env')
                open(env_file, 'a').close()

        set_key(env_file, 'API_KEY', new_key)
        os.environ['API_KEY'] = new_key
        load_dotenv(env_file, override=True)
        return True
    except Exception:
        return False