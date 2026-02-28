import os
from moviepy import VideoFileClip, AudioFileClip
from gtts import gTTS

def build_video(video_path, script_text):
    print("🎬 AI Engine Started...")
    
    try:
        # 1. Setup Folders
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        media_folder = os.path.join(base_dir, 'media')
        os.makedirs(media_folder, exist_ok=True)
        
        # 2. Generate the AI Voice!
        print("🗣️ Generating AI Voiceover...")
        audio_filename = "temp_voice.mp3"
        audio_path = os.path.join(media_folder, audio_filename)
        
        tts = gTTS(text=script_text, lang='en', slow=False)
        tts.save(audio_path)
        
        # 3. Load the Video and the new Audio
        print("✂️ Mixing Video and Audio...")
        video_clip = VideoFileClip(video_path)
        voice_clip = AudioFileClip(audio_path)
        
        # 4. Trim the video to match the exact length of the voiceover!
        final_video = video_clip.subclipped(0, voice_clip.duration)
        
        # 5. Attach the AI voice to the video
        final_video = final_video.with_audio(voice_clip)
        
        # 6. Export the final masterpiece
        output_filename = "final_output.mp4"
        output_path = os.path.join(media_folder, output_filename)
        
        print("⏳ Rendering Final Video...")
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
        
        # Clean up the temporary mp3 file
        voice_clip.close()
        video_clip.close()
        os.remove(audio_path)
        
        print("✅ AI Engine Finished Successfully!")
        return output_filename
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        return None