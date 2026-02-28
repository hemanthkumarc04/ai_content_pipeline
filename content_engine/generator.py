import os
import requests
from moviepy import VideoFileClip, AudioFileClip

def build_video(video_path, script_text):
    print("🎬 Pro AI Engine Started...")
    
    try:
        # 1. Setup Folders
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        media_folder = os.path.join(base_dir, 'media')
        os.makedirs(media_folder, exist_ok=True)
        
        # 2. ElevenLabs Configuration
        print("🗣️ Downloading Pro ElevenLabs Voiceover...")
        audio_path = os.path.join(media_folder, "temp_voice.mp3")
        
        API_KEY = "sk_46e120cad19a8df9666fc66885e7509e4ff3e2fa595790fc"
        
        # UPDATED: Using "Adam" (The most reliable Pro voice)
        VOICE_ID = "pNInz6obpgDQGcFmaJgB" 
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": API_KEY
        }
        
        data = {
            "text": script_text,
            "model_id": "eleven_turbo_v2_5", 
            "voice_settings": {
                "stability": 0.35,            # Low stability = More emotion/excitement
                "similarity_boost": 0.8,
                "style": 0.5,
                "use_speaker_boost": True
            }
        }
        
        # 3. Get Audio
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ ElevenLabs API Error: {response.text}")
            return None
            
        with open(audio_path, 'wb') as f:
            f.write(response.content)
        
        # 4. Mix Video and Audio
        print("✂️ Mixing Video and Audio...")
        video_clip = VideoFileClip(video_path)
        voice_clip = AudioFileClip(audio_path)
        
        final_video = video_clip.subclipped(0, voice_clip.duration)
        final_video = final_video.with_audio(voice_clip)
        
        # 5. Export
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
        return None