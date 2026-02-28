import os
from moviepy import VideoFileClip

def build_video(video_path, script_text):
    print("🎬 MoviePy Engine Started...")
    
    try:
        # 1. Load the uploaded video into MoviePy
        clip = VideoFileClip(video_path)
        
        # 2. Trim the video to 5 seconds
        duration = min(5, clip.duration)
        edited_clip = clip.subclipped(0, duration)
        
        # 3. Define where to save the final generated video
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # --- THE FIX: Tell Python to create the 'media' folder if it doesn't exist ---
        media_folder = os.path.join(base_dir, 'media')
        os.makedirs(media_folder, exist_ok=True)
        # ----------------------------------------------------------------------------
        
        output_filename = "final_output.mp4"
        output_path = os.path.join(media_folder, output_filename)
        
        # 4. Render and export the final video!
        edited_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
        
        print("✅ MoviePy Engine Finished Successfully!")
        return output_filename
        
    except Exception as e:
        print(f"❌ Error during video processing: {e}")
        return None