from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from .generator import build_video


def home_page(request):
    if request.method == 'POST':
        script_text = request.POST.get('script')
        uploaded_video = request.FILES.get('background_video')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if script_text and uploaded_video:
            fs = FileSystemStorage()
            filename = fs.save(uploaded_video.name, uploaded_video)
            video_path = fs.path(filename)

            print("⏳ Sending video to MoviePy for processing...")

            final_video_name = build_video(video_path, script_text)

            if final_video_name:
                video_url = f"/media/{final_video_name}"
                if is_ajax:
                    return JsonResponse({'success': True, 'video_url': video_url})
                return render(request, 'index.html', {
                    'message': 'Video processed successfully!',
                    'message_type': 'success',
                    'video_url': video_url,
                })
            else:
                if is_ajax:
                    return JsonResponse({'success': False, 'error': 'Processing failed. Please try again.'})
                return render(request, 'index.html', {
                    'message': 'Something went wrong during processing.',
                    'message_type': 'error',
                })

    return render(request, 'index.html')