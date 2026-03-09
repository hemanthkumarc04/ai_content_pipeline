import os
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .generator import build_video, build_promo_video

def home_page(request):
    context = {}
    
    if request.method == 'POST':
        fs = FileSystemStorage()
        action = request.POST.get('action')
        script_text = request.POST.get('script')

        try:
            # ==========================================
            # ✂️ STANDARD ENGINE (Multi-Video Montage)
            # ==========================================
            if action == 'standard':
                video_files = request.FILES.getlist('videos') 
                if video_files and script_text:
                    video_paths = []
                    for video in video_files:
                        v_name = fs.save(video.name, video)
                        video_paths.append(fs.path(v_name))
                    
                    output_filename = build_video(video_paths, script_text)
                    
                    if output_filename:
                        context['video_url'] = fs.url(output_filename)
                        context['success_message'] = f"Successfully stitched {len(video_paths)} videos!"
                    else:
                        context['error_message'] = "Standard generation failed. Check your terminal for API or MoviePy errors."

            # ==========================================
            # 📸 PROMO ENGINE (Photos + Music + Voice)
            # ==========================================
            elif action == 'promo':
                photo_files = request.FILES.getlist('photos')
                music_file = request.FILES.get('music')
                
                if photo_files and music_file and script_text:
                    photo_paths = []
                    for photo in photo_files:
                        p_name = fs.save(photo.name, photo)
                        photo_paths.append(fs.path(p_name))
                        
                    m_name = fs.save(music_file.name, music_file)
                    music_path = fs.path(m_name)
                    
                    output_filename = build_promo_video(photo_paths, music_path, script_text)
                    
                    if output_filename:
                        context['video_url'] = fs.url(output_filename)
                        context['success_message'] = f"Promo Video generated using {len(photo_paths)} photos!"
                    else:
                        context['error_message'] = "Promo generation failed. Check your terminal for errors."

        except Exception as e:
            context['error_message'] = f"Server Error: {str(e)}"

    return render(request, 'index.html', context)