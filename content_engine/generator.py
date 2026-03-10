import os
import traceback
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    VideoFileClip, AudioFileClip, ImageClip,
    concatenate_videoclips, CompositeAudioClip, CompositeVideoClip
)
from dotenv import load_dotenv, find_dotenv, set_key
from gtts import gTTS

# Map UI language codes → gTTS language codes
GTTS_LANG_MAP = {
    'en': 'en', 'hi': 'hi', 'kn': 'kn', 'es': 'es', 'fr': 'fr',
    'de': 'de', 'it': 'it', 'pt': 'pt', 'ru': 'ru', 'ja': 'ja',
    'ko': 'ko', 'zh': 'zh-CN', 'ta': 'ta', 'te': 'te', 'ml': 'ml',
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
    """Generates audio via ElevenLabs using the V3 model for regional Indian languages."""
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
        "model_id": "eleven_v3", # Upgraded to V3 for Kannada/Tamil support
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

# ─── PURE PYTHON SUBTITLE ENGINE (No ImageMagick Required) ────────────────────

def _create_subtitle_image(text, video_width, duration, lang='en'):
    """Creates a transparent PNG image, routing to bundled Google Fonts for Indian scripts."""
    # Increased canvas height to 200 to accommodate larger fonts
    img = Image.new('RGBA', (int(video_width), 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font_size = 75  # 🚀 MASSIVE SIZE INCREASE
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        if lang == 'kn':
            font = ImageFont.truetype(os.path.join(current_dir, "NotoSansKannada-Bold.ttf"), font_size)
        elif lang == 'ta':
            font = ImageFont.truetype(os.path.join(current_dir, "NotoSansTamil-Bold.ttf"), font_size)
        elif lang in ['hi', 'te', 'ml']:
            # Absolute path to Windows Native Indian Font
            font = ImageFont.truetype(r"C:\Windows\Fonts\nirmala.ttf", font_size)
        else:
            # Absolute path to Windows Native Latin Font
            font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", font_size)
    except Exception as e:
        # If you see this in your terminal, your font files are missing!
        print(f"\n❌ FATAL FONT ERROR: {e}")
        print("❌ FALLING BACK TO 11px DEFAULT. TEXT WILL BE TINY.\n")
        font = ImageFont.load_default()

    # Smart math to center the text perfectly
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]
    
    x = (video_width - text_w) / 2
    y = (200 - text_h) / 2 # Center vertically in the new 200px canvas

    # Draw a thicker black outline for the larger text
    outline_color = (0, 0, 0, 255)
    for offset_x in [-3, -2, 2, 3]:
        for offset_y in [-3, -2, 2, 3]:
            draw.text((x + offset_x, y + offset_y), text, font=font, fill=outline_color)
    
    # Draw the main yellow text
    draw.text((x, y), text, font=font, fill=(255, 255, 0, 255))
    
    img_array = np.array(img)
    return ImageClip(img_array).with_duration(duration)

def _create_subtitle_clips(text, duration, video_w, video_h, lang='en'):
    """Splits text into chunks and converts them into timed Pillow ImageClips."""
    words = text.split()
    if not words:
        return []
        
    chunks = []
    chunk = []
    for word in words:
        chunk.append(word)
        if len(chunk) >= 5:
            chunks.append(" ".join(chunk))
            chunk = []
    if chunk:
        chunks.append(" ".join(chunk))
        
    time_per_chunk = duration / max(1, len(chunks))
    
    subs = []
    current_time = 0
    for chunk_text in chunks:
        # Pass the language down to the image creator
        txt_clip = _create_subtitle_image(chunk_text, video_w, time_per_chunk, lang)
        txt_clip = txt_clip.with_start(current_time).with_position(('center', int(video_h * 0.8)))
        subs.append(txt_clip)
        current_time += time_per_chunk
        
    return subs

# ──────────────────────────────────────────────────────────────────────────────

def _loop_video_to_duration(video_clip, target_duration):
    """Loops or trims a video clip to exactly match target_duration."""
    import math
    if video_clip.duration >= target_duration:
        start_time = max(0, (video_clip.duration - target_duration) / 2)
        return video_clip.subclipped(start_time, start_time + target_duration)
    
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

        # 1. Generate Voiceover
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

        # 3. Subtitle Overlay using Pure Python Engine
        subtitle_clips = _create_subtitle_clips(script_text, total_audio_duration, stitched_video.w, stitched_video.h, lang)
        if subtitle_clips:
            print(f"📝 Adding {len(subtitle_clips)} dynamic subtitle chunks overlay...")
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

        print("🎵 Mixing audio tracks...")
        bg_music_raw = AudioFileClip(bg_music_path)
        bg_music = _loop_audio_to_duration(bg_music_raw, total_duration).with_volume_scaled(0.1)
        final_audio = CompositeAudioClip([bg_music, voice_clip])

        print("📸 Animating photos...")
        time_per_photo = total_duration / len(photo_paths)
        image_clips = [_animate_photo_locally(p, time_per_photo) for p in photo_paths]

        final_video = concatenate_videoclips(image_clips, method="compose").with_audio(final_audio)

        output_filename = "final_promo_output.mp4"
        output_path = os.path.join(media_folder, output_filename)
        print("⏳ Rendering Promo Video...")
        final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

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