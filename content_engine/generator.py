import os
import traceback
import requests
from moviepy import VideoFileClip, AudioFileClip, ImageClip, concatenate_videoclips, CompositeAudioClip, CompositeVideoClip
from dotenv import load_dotenv, find_dotenv, set_key
from gtts import gTTS


def _get_api_key():
    """Load API_KEY from environment variables (supports Render + .env)."""
    key = os.environ.get('API_KEY')
    if key:
        return key
    
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


# ==========================================
# ✂️ STANDARD ENGINE (Montage Mode)
# ==========================================

def build_video(video_paths, script_text):
    """Standard video processor (Snippets multiple videos from the middle into a montage + AI voice)."""
    print("🎬 Pro AI Engine Started (Montage Mode)...")

    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        media_folder = os.path.join(base_dir, "media")
        os.makedirs(media_folder, exist_ok=True)

        audio_path = os.path.join(media_folder, "temp_voice.mp3")

        print("🗣️ Generating voiceover...")
        if not _tts_elevenlabs(script_text, audio_path):
            print("🔄 Falling back to Google TTS...")
            if not _tts_gtts(script_text, audio_path):
                print("❌ All TTS engines failed. Cannot generate video.")
                return None

        print("✂️ Chopping Videos into Dynamic Snippets...")
        voice_clip = AudioFileClip(audio_path)
        total_audio_duration = voice_clip.duration
        
        # 1. THE MONTAGE MATH: Divide audio length by number of uploaded videos
        num_videos = len(video_paths)
        time_per_clip = total_audio_duration / num_videos
        
        clips = []
        for path in video_paths:
            clip = VideoFileClip(path).resized(height=720)
            
            # 2. Safety Check: Determine how much time we can actually extract
            actual_snippet_time = min(time_per_clip, clip.duration)
            
            # 3. Middle Extraction Math: Find the center of the video to start the cut
            start_time = max(0, (clip.duration - actual_snippet_time) / 2)
            end_time = start_time + actual_snippet_time
            
            # 4. Cut the snippet from the middle
            snippet = clip.subclipped(start_time, end_time)
            clips.append(snippet)
            
        # 5. Stitch the new, short snippets together
        stitched_video = concatenate_videoclips(clips, method="compose")

        # 6. Layer the audio and lock the final duration to match the voiceover perfectly
        final_video = stitched_video.with_audio(voice_clip).with_duration(total_audio_duration)

        output_filename = "final_output.mp4"
        output_path = os.path.join(media_folder, output_filename)

        print("⏳ Rendering Final Montage Video...")
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")

        # Clean up memory
        voice_clip.close()
        for c in clips:
            c.close()
        stitched_video.close()
        if os.path.exists(audio_path):
            os.remove(audio_path)

        print("✅ Pro AI Engine Finished Successfully!")
        return output_filename

    except Exception as e:
        print(f"❌ Error during processing: {e}")
        traceback.print_exc()
        return None


# ==========================================
# 🚀 PROMO ENGINE (Photos + Music + AI)
# ==========================================

def _animate_photo_locally(photo_path, duration):
    """
    Creates a cinematic zoom-in animation locally using pure Python math.
    No paid APIs required!
    """
    print(f"🎥 Applying cinematic zoom to {photo_path}...")
    
    # 1. Load the image and set it to 720p height
    clip = ImageClip(photo_path).with_duration(duration)
    clip = clip.resized(height=720) 
    
    # 2. Math function: grows image by 3% every second
    def zoom(t):
        return 1 + 0.03 * t
        
    zoomed_clip = clip.resized(zoom)
    
    # 3. Center it on a fixed canvas so the video resolution doesn't warp
    w, h = clip.size
    final_clip = CompositeVideoClip([zoomed_clip.with_position('center')], size=(w, h))
    
    return final_clip


def build_promo_video(photo_paths, bg_music_path, script_text):
    """Generates an animated commercial from photos, AI voiceover, and background music."""
    print("🎬 Starting AI Promo Video Engine...")
    
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        media_folder = os.path.join(base_dir, "media")
        os.makedirs(media_folder, exist_ok=True)
        
        audio_path = os.path.join(media_folder, "temp_promo_voice.mp3")
        
        # 1. Generate Voiceover
        print("🗣️ Generating Promo Voiceover...")
        if not _tts_elevenlabs(script_text, audio_path):
            print("🔄 Falling back to Google TTS...")
            if not _tts_gtts(script_text, audio_path):
                print("❌ All TTS engines failed.")
                return None
                
        voice_clip = AudioFileClip(audio_path)
        total_duration = voice_clip.duration
        
        # 2. Smart Audio Mixing
        print("🎵 Mixing Audio Tracks...")
        bg_music = AudioFileClip(bg_music_path)
        
        # Loop/trim to match voiceover, and drop volume to 10%
        bg_music = bg_music.subclipped(0, min(total_duration, bg_music.duration)).with_volume_scaled(0.1) 
        final_audio = CompositeAudioClip([bg_music, voice_clip])
        
        # 3. Animate the Photos
        print("📸 Stitching and Animating Photos...")
        time_per_photo = total_duration / len(photo_paths) 
        
        image_clips = []
        for photo in photo_paths:
            animated_clip = _animate_photo_locally(photo, time_per_photo)
            image_clips.append(animated_clip)
            
        final_video = concatenate_videoclips(image_clips, method="compose")
        final_video = final_video.with_audio(final_audio)
        
        # 4. Export the Masterpiece
        output_filename = "final_promo_output.mp4"
        output_path = os.path.join(media_folder, output_filename)
        
        print("⏳ Rendering Final Promo Video...")
        final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
        
        # 5. Clean up Memory
        voice_clip.close()
        bg_music.close()
        final_video.close()
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        print("✅ Promo Engine Finished Successfully!")
        return output_filename
        
    except Exception as e:
        print(f"❌ Error during promo processing: {e}")
        traceback.print_exc()
        return None