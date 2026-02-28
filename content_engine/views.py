from django.shortcuts import render
from django.core.files.storage import FileSystemStorage

def home_page(request):
    # Check if the user just clicked the "Generate Video" button
    if request.method == 'POST':
        # 1. Catch the text script
        script_text = request.POST.get('script')
        
        # 2. Catch the uploaded background video
        uploaded_video = request.FILES.get('background_video')
        
        # 3. If both were provided, let's save the video temporarily
        if script_text and uploaded_video:
            fs = FileSystemStorage()
            # This saves the file into your media folder
            filename = fs.save(uploaded_video.name, uploaded_video)
            
            # Let's print it to the terminal to prove it worked!
            print("====================================")
            print("🎉 SUCCESS! Received your script:")
            print(script_text)
            print("📁 Saved background video as:", filename)
            print("====================================")
            
            # Send a success message back to the web page
            return render(request, 'index.html', {'message': 'Data received successfully! Check your VS Code terminal.'})
            
    # If they are just visiting the page normally, show the empty form
    return render(request, 'index.html')