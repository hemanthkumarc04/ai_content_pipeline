import os
import glob
import traceback
import requests
from moviepy import (
    VideoFileClip, AudioFileClip, ImageClip,
    concatenate_videoclips, CompositeAudioClip, CompositeVideoClip, TextClip
)
from dotenv import load_dotenv, find_dotenv, set_key
from gtts import gTTS

# ─── ImageMagick Auto-Detection ────────────────────────────────────────────────
# Searches for any installed ImageMagick version automatically on Windows.
def _find_imagemagick():
    search_patterns = [
        r"C:\Program Files\ImageMagick*\magick.exe",
        r"C:\Program Files (x86)\ImageMagick*\magick.exe",
    ]
    for pattern in search_patterns:
        matches = glob.glob(pattern)
        if matches:
            return matches[0]
    return None

_im_path = _find_imagemagick()
if _im_path:
    os.environ["IMAGEMAGICK_BINARY"] = _im_path
    print(f"✅ ImageMagick found: {_im_path}")
else:
    print("⚠️  ImageMagick not found — subtitle TextClip will be skipped.")

# Map UI language codes → gTTS language codes
GTTS_LANG_MAP = {
    'en': 'en',
    'hi': 'hi',
    'kn': 'kn',
    'es': 'es',
    'fr': 'fr',
    'de': 'de',
    'it': 'it',
    'pt': 'pt',
    'ru': 'ru',
    'ja': 'ja',
    'ko': 'ko',
    'zh': 'zh-CN',
    'ta': 'ta',
    'te': 'te',
    'ml': 'ml',
}


def _get_api_key():
    """Load API_KEY from environment variables (supports Render + .env)."""
    key = os.environ.get('API_KEY')
    if key:
        return key
    env_path = find_dotenv()
    if env_path:
        load_dotenv(env_path)
    return os.getenv('API_KEY')


def _tts_elevenlabs(script_text, audio_path, voice_choice='male'):
    """Generates audio via ElevenLabs — Adam (male) or Bella (female)."""
    API_KEY = _get_api_key()
    if not API_KEY:
        print("⚠️ API_KEY not found — skipping ElevenLabs.")
        return False

    # Adam = male, Bella = female
    VOICE_ID = "pNInz6obpgDQGcFmaJgB" if voice_choice == 'male' else "EXAVITQu4vr4PUHQRBy1"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": API_KEY,
    }
    data = {
        "text": script_text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.8},
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        if response.status_code == 200:
            with open(audio_path, "wb") as f:
                f.write(response.content)
            print("✅ ElevenLabs voiceover downloaded.")
            return True
        print(f"⚠️ ElevenLabs API Error ({response.status_code}): {response.text[:200]}")
        return False
    except Exception as e:
        print(f"⚠️ ElevenLabs request failed: {e}")
        return False


def _tts_gtts(script_text, audio_path, lang='en'):
    """Fallback TTS using Google gTTS. Supports multilingual output."""
    try:
        gtts_lang = GTTS_LANG_MAP.get(lang, 'en')
        tts = gTTS(text=script_text, lang=gtts_lang, slow=False)
        tts.save(audio_path)
        print(f"✅ gTTS voiceover generated (lang={gtts_lang}) as fallback.")
        return True
    except Exception as e:
        print(f"❌ gTTS also failed: {e}")
        return False


def set_api_key(new_key, env_file=None):
    """Update or create API_KEY in the project's .env file."""
    try:
        if env_file is None:
            env_file = find_dotenv()
            if not env_file:
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                env_file = os.path.join(project_root, '.env')
                open(env_file, 'a').close()
        set_key(env_file, 'API_KEY', new_key)
        os.environ['API_KEY'] = new_key
        load_dotenv(env_file, override=True)
        return True
    except Exception:
        return False


def _create_subtitle_clips(text, duration, video_w, video_h):
    """
    Safely creates a sequence of subtitle TextClips synchronized roughly to the audio.
    Returns an empty list if ImageMagick is missing or creation fails.
    """
    if not os.environ.get("IMAGEMAGICK_BINARY"):
        print("⚠️ Skipping subtitles — ImageMagick not configured.")
        return []
    
    words = text.split()
    if not words:
        return []
        
    # Group words into chunks of ~4-5 words
    chunks = []
    chunk = []
    for word in words:
        chunk.append(word)
        if len(chunk) >= 5:
            chunks.append(" ".join(chunk))
            chunk = []
    if chunk:
        chunks.append(" ".join(chunk))
        
    # Calculate time per character to estimate subtitle synced timings
    num_chars = sum(len(c) for c in chunks)
    time_per_char = duration / max(1, num_chars)
    
    subs = []
    current_time = 0
    for chunk_text in chunks:
        chunk_duration = len(chunk_text) * time_per_char
        try:
            subtitle = TextClip(
                text=chunk_text,
                font_size=45,
                color='white',
                stroke_color='black',
                stroke_width=2.5,
                method='caption',
                align='center',
                size=(int(video_w * 0.8), None),
            ).with_duration(chunk_duration).with_position(('center', int(video_h * 0.8)))
            subs.append(subtitle)
        except Exception as e:
            print(f"⚠️ TextClip subtitle chunk creation failed: {e}")
        current_time += chunk_duration
        
    return subs

def _loop_video_to_duration(video_clip, target_duration):
    """Loops or trims a video clip to exactly match target_duration."""
    import math
    if video_clip.duration >= target_duration:
        start_time = max(0, (video_clip.duration - target_duration) / 2)
        return video_clip.subclipped(start_time, start_time + target_duration)
    
    # Need to loop if it's too short
    loops_needed = math.ceil(target_duration / video_clip.duration)
    looped = concatenate_videoclips([video_clip] * loops_needed, method="compose")
    return looped.subclipped(0, target_duration)



# ==========================================
# ✂️ STANDARD ENGINE (Montage Mode + Subtitles + Voice)
# ==========================================

def build_video(video_paths, script_text, voice_choice='male', lang='en'):
    """Montage engine: stitches multiple video clips, adds AI voiceover + subtitles."""
    print(f"🎬 AI Montage Engine Started | Voice: {voice_choice} | Lang: {lang}")
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        media_folder = os.path.join(base_dir, "media")
        os.makedirs(media_folder, exist_ok=True)
        audio_path = os.path.join(media_folder, "temp_voice.mp3")

        # 1. Generate Voiceover (ElevenLabs → gTTS fallback)
        print("🗣️ Generating voiceover...")
        used_engine = "ElevenLabs"
        if not _tts_elevenlabs(script_text, audio_path, voice_choice):
            print("🔄 Falling back to gTTS...")
            used_engine = "gTTS (Fallback)"
            if not _tts_gtts(script_text, audio_path, lang):
                print("❌ All TTS engines failed.")
                return None, None

        voice_clip = AudioFileClip(audio_path)
        total_audio_duration = voice_clip.duration

        # 2. Build Montage Clips
        print("✂️ Cutting video snippets...")
        num_videos = len(video_paths)
        time_per_clip = total_audio_duration / num_videos
        clips = []
        for path in video_paths:
            clip = VideoFileClip(path).resized(height=720)
            snippet = _loop_video_to_duration(clip, time_per_clip)
            clips.append(snippet)

        stitched_video = concatenate_videoclips(clips, method="compose")

        # 3. Subtitle Overlay
        subtitle_clips = _create_subtitle_clips(script_text, total_audio_duration, stitched_video.w, stitched_video.h)
        if subtitle_clips:
            print(f"📝 Adding {len(subtitle_clips)} subtitle chunks overlay...")
            final_video = CompositeVideoClip([stitched_video] + subtitle_clips).with_audio(voice_clip)
        else:
            final_video = stitched_video.with_audio(voice_clip).with_duration(total_audio_duration)

        # 4. Export
        output_filename = "final_output.mp4"
        output_path = os.path.join(media_folder, output_filename)
        print("⏳ Rendering Montage Video...")
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)

        # 5. Cleanup
        voice_clip.close()
        for c in clips:
            c.close()
        stitched_video.close()
        if os.path.exists(audio_path):
            os.remove(audio_path)

        print("✅ Montage Engine Finished!")
        return output_filename, used_engine

    except Exception:
        traceback.print_exc()
        return None, None


# ==========================================
# 🚀 PROMO ENGINE (Photos + Music + Voice)
# ==========================================

def _animate_photo_locally(photo_path, duration):
    """Creates a cinematic zoom-in animation from a still image."""
    clip = ImageClip(photo_path).with_duration(duration).resized(height=720)
    zoomed_clip = clip.resized(lambda t: 1 + 0.03 * t)
    w, h = clip.size
    return CompositeVideoClip([zoomed_clip.with_position('center')], size=(w, h))


def _loop_audio_to_duration(audio_clip, target_duration):
    """Loops or trims an audio clip to exactly match target_duration."""
    import math
    from moviepy import concatenate_audioclips
    if audio_clip.duration >= target_duration:
        return audio_clip.subclipped(0, target_duration)
    # Need to loop
    loops_needed = math.ceil(target_duration / audio_clip.duration)
    looped = concatenate_audioclips([audio_clip] * loops_needed)
    return looped.subclipped(0, target_duration)


def build_promo_video(photo_paths, bg_music_path, script_text, voice_choice='male', lang='en'):
    """Promo engine: animated photos + background music + AI voiceover."""
    print(f"🎬 AI Promo Engine Started | Voice: {voice_choice} | Lang: {lang}")
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        media_folder = os.path.join(base_dir, "media")
        os.makedirs(media_folder, exist_ok=True)
        audio_path = os.path.join(media_folder, "temp_promo_voice.mp3")

        # 1. Generate Voiceover
        print("🗣️ Generating promo voiceover...")
        used_engine = "ElevenLabs"
        if not _tts_elevenlabs(script_text, audio_path, voice_choice):
            print("🔄 Falling back to gTTS...")
            used_engine = "gTTS (Fallback)"
            if not _tts_gtts(script_text, audio_path, lang):
                print("❌ All TTS engines failed.")
                return None, None

        voice_clip = AudioFileClip(audio_path)
        total_duration = voice_clip.duration

        # 2. Smart Audio Mixing — loop bg music if shorter than voiceover
        print("🎵 Mixing audio tracks...")
        bg_music_raw = AudioFileClip(bg_music_path)
        bg_music = _loop_audio_to_duration(bg_music_raw, total_duration).with_volume_scaled(0.1)
        final_audio = CompositeAudioClip([bg_music, voice_clip])

        # 3. Animate Photos
        print("📸 Animating photos...")
        time_per_photo = total_duration / len(photo_paths)
        image_clips = [_animate_photo_locally(p, time_per_photo) for p in photo_paths]

        final_video = concatenate_videoclips(image_clips, method="compose").with_audio(final_audio)

        # 4. Export
        output_filename = "final_promo_output.mp4"
        output_path = os.path.join(media_folder, output_filename)
        print("⏳ Rendering Promo Video...")
        final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

        # 5. Cleanup
        voice_clip.close()
        bg_music_raw.close()
        final_video.close()
        if os.path.exists(audio_path):
            os.remove(audio_path)

        print("✅ Promo Engine Finished!")
        return output_filename, used_engine

    except Exception:
        traceback.print_exc()
        return None, None