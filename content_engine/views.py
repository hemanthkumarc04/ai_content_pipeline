from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .generator import build_video # <-- Import your new engine here!

def home_page(request):
    if request.method == 'POST':
        script_text = request.POST.get('script')
        uploaded_video = request.FILES.get('background_video')
        
        if script_text and uploaded_video:
            fs = FileSystemStorage()
            filename = fs.save(uploaded_video.name, uploaded_video)
            
            # Get the exact file path on your computer
            video_path = fs.path(filename)
            
            print("⏳ Sending video to MoviePy for processing...")
            
            # ---> Trigger the video engine! <---
            final_video_name = build_video(video_path, script_text)
            
            if final_video_name:
                message = "✅ Video processed successfully!"
                # Create the web link to the video
                video_url = f"/media/{final_video_name}" 
                
                # Send BOTH the message and the video link to the HTML
                return render(request, 'index.html', {'message': message, 'video_url': video_url})
            else:
                message = "❌ Something went wrong during processing."
                return render(request, 'index.html', {'message': message})
        
    return render(request, 'index.html')