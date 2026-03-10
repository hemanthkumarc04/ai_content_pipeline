import os
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from deep_translator import GoogleTranslator  # New library for translation
from .generator import build_video, build_promo_video

def home_page(request):
    context = {}
    
    if request.method == 'POST':
        fs = FileSystemStorage()
        action = request.POST.get('action')
        original_script = request.POST.get('script')
        
        # New Features: Get language and voice choices from the HTML
        target_lang = request.POST.get('language', 'en')
        voice_choice = request.POST.get('voice', 'male')

        try:
            # --- FEATURE: TRANSLATION ---
            # If user selects anything other than English, translate the script first
            final_script = original_script
            if target_lang != 'en' and original_script:
                try:
                    final_script = GoogleTranslator(source='auto', target=target_lang).translate(original_script)
                    context['translated_script'] = final_script  # To show on the UI
                except Exception as trans_err:
                    print(f"Translation Error: {trans_err}")
                    final_script = original_script  # Fallback to original script

            # ==========================================
            # ✂️ STANDARD ENGINE (Multi-Video Montage)
            # ==========================================
            if action == 'standard':
                video_files = request.FILES.getlist('videos') 
                if video_files and final_script:
                    video_paths = []
                    for video in video_files:
                        v_name = fs.save(video.name, video)
                        video_paths.append(fs.path(v_name))
                    
                    # Pass the final_script (translated) and voice_choice to the generator
                    result = build_video(video_paths, final_script, voice_choice, lang=target_lang)
                    
                    if result and result[0]:
                        output_filename, used_engine = result
                        context['video_url'] = fs.url(output_filename)
                        if used_engine == "gTTS (Fallback)":
                            context['success_message'] = f"Video generated in {target_lang}! (⚠️ ElevenLabs Voice failed. Fell back to default generic voice)"
                        else:
                            context['success_message'] = f"Successfully generated video with premium {target_lang} voice!"
                    else:
                        context['error_message'] = "Standard generation failed. Check ImageMagick or API logs."

            # ==========================================
            # 📸 PROMO ENGINE (Photos + Music + Voice)
            # ==========================================
            elif action == 'promo':
                photo_files = request.FILES.getlist('photos')
                music_file = request.FILES.get('music')
                
                if photo_files and music_file and final_script:
                    photo_paths = []
                    for photo in photo_files:
                        p_name = fs.save(photo.name, photo)
                        photo_paths.append(fs.path(p_name))
                        
                    m_name = fs.save(music_file.name, music_file)
                    music_path = fs.path(m_name)
                    
                    # Pass the final_script and voice_choice to the promo generator
                    result = build_promo_video(photo_paths, music_path, final_script, voice_choice, lang=target_lang)
                    
                    if result and result[0]:
                        output_filename, used_engine = result
                        context['video_url'] = fs.url(output_filename)
                        if used_engine == "gTTS (Fallback)":
                            context['success_message'] = f"Promo generated in {target_lang}! (⚠️ ElevenLabs Voice failed. Fell back to default generic voice)"
                        else:
                            context['success_message'] = f"Successfully generated Promo with premium {target_lang} voice!"
                    else:
                        context['error_message'] = "Promo generation failed. Check Logs."

        except Exception as e:
            import traceback
            traceback.print_exc()
            context['error_message'] = f"Server Error: {str(e)}"

    return render(request, 'index.html', context)