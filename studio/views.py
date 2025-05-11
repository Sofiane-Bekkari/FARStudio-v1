import datetime
import uuid
from django.shortcuts import redirect, render
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import os
from django.conf import settings
# TRANSCRIPT
import whisper
# PDF
from weasyprint import HTML
from django.template.loader import render_to_string
# OUTSIDE Script
from transcripte_audio import tran_audio

# Create your views here.
def index_page(request):
    return HttpResponse("Hello, this FARStudio by Sofiane.")

"""""""""""""""""""""""""""
NOTE AUTHENTICATION 
"""""""""""""""""""""""""""
def custom_logout(request):
    logout(request)

    messages.error(request, 'Vous êtes déconnecté')
    return redirect('account_login')

# REQUIRE AUTHENTICATION
@login_required
def index(request):

    matched_files = []
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    media_url = settings.MEDIA_URL + 'uploads/'

    if os.path.exists(upload_dir):
        files = os.listdir(upload_dir)
        webm_files = [f for f in files if f.endswith('.webm')]

        for webm in webm_files:
            # SETP 1 RECORD
            base_name = os.path.splitext(webm)[0]
            # SETP 2 TRANSCRIPT
            txt_name = base_name + '.txt'
            # SETP 3 AI SUMMARY
            edited_txt_name = base_name + '_ai_summary.txt'

        matched_files.append({
            'audio': media_url + webm,
            'transcript': media_url + txt_name if txt_name in files else None,
            'ai_summary': media_url + edited_txt_name if edited_txt_name in files else None,
        })

    print(f'MATCHED FILE >>> {matched_files}')


    return render(request, 'studio/index.html', {
                                                  'matched_files':matched_files }) # PASS FILES as LIST


# NOTE TESTING RECORDING AUDIO
@csrf_exempt  # Not recommended in production – use csrf token properly
def upload_audio(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']
        # KEEP OLD RECORD AND NOT OVERWRITE

        # Generate timestamp-based filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')  # e.g., 20250502_153045
        print(f'THIS TIPESTAPM/ {timestamp}')
        file_ext = os.path.splitext(audio_file.name)[-1] or '.webm'
        filename = f"{timestamp}{file_ext}"

        save_path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, 'wb+') as destination:
            for chunk in audio_file.chunks():
                destination.write(chunk)
        
        # Build media URL
        file_url = f"{settings.MEDIA_URL}uploads/{filename}"

        # NOTE we try to add Transcript after record  ON TEST
        tran_audio(filename)

        return JsonResponse({'status': 'success', 'url': file_url})

        #return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)


# NOTE SECOND STEP TO TRANSCRIPTE AUDIO 
def transcript_audio_view(request, filename):
    audio_path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)

    if not os.path.exists(audio_path):
        return JsonResponse({'status': 'error', 'message': 'Audio file not found'}, status=404)

    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    transcription_text = result['text']

    # Save the transcription as a text file
    base_name, _ = os.path.splitext(filename)
    transcript_filename = base_name + ".txt"
    transcript_path = os.path.join(settings.MEDIA_ROOT, 'uploads', transcript_filename)

    with open(transcript_path, 'w', encoding='utf-8') as f:
        f.write(transcription_text)

    
    return JsonResponse({
        'status': 'success',
        'transcription': transcription_text,
        'transcription_url': f"{settings.MEDIA_URL}uploads/{transcript_filename}"
    })


# NOTE START WITH AI ANAYLSIS WITH Phi3-mini
from django.shortcuts import render
from .ollama_utility import analyze_text_with_phi3

def analyze_transcript_view(request, filename):
    path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)
    with open(path, 'r', encoding='utf-8') as f:
        transcript_text = f.read()

    prompt = f"Summarize the following transcript and list 5 key topics:\n\n{transcript_text}"
    #analysis = analyze_text_with_phi3(prompt)

    return render(request, 'studio/analysis_page.html', {
        'filename': filename,
        #'analysis': analysis
    })

def analyze_transcript_process(request, filename):
    path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)
    with open(path, 'r', encoding='utf-8') as f:
        transcript_text = f.read()

    # ASK AI WITH GOOD FR ARGEMENT AS PROMPT
    prompt = f"Résumez la transcription suivante et énumérez 5 sujets clés:\n\n{transcript_text}"
    analysis = analyze_text_with_phi3(prompt)
    # NOTE FOR QUICK TEST
    #analysis = transcript_text

    # SPLIT BY '.'
    sentences = [s.strip() + '.' for s in analysis.split('.') if s.strip()]

    print(f'sentences >> {sentences}')
    return render(request, 'studio/partials/analysis_result.html', {
        'filename': filename,
        'analysis': analysis,
        'sentences': sentences,
    })

# NOTE // save editable AI Analysis
@csrf_exempt
def save_edited_result(request):
    if request.method == 'POST':
        filename = request.POST.get('filename')  # e.g., '20250504_200922'
        content = request.POST.get('content')    # the edited text
        
        base_name, _ = os.path.splitext(filename)
        
        if filename.endswith('_ai_summary.txt'):
            save_path = os.path.join(settings.MEDIA_ROOT, 'uploads', f'{filename}')
            
            filename_url = os.path.basename(save_path)
        else:
            save_path = os.path.join(settings.MEDIA_ROOT, 'uploads', f'{base_name}_ai_summary.txt')
            
            filename_url = os.path.basename(save_path)


        print(f'URL fileNAME // {filename_url}')
        print(f'BASE NAME // {base_name}')
        print(f'SAVE PATH // {save_path}')
        print(f'CONTENT // {content}')
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        messages.success(request, f'You have been save this file!')
        return redirect('ai_summary', filename_url)
        return HttpResponse('<div style="color: green; font-weight: bold;">You have successfully uploaded your file!</div>')
        #return JsonResponse({'status': 'success', 'path': save_path})
    return JsonResponse({'status': 'error'}, status=400) 

# NOTE // save editable AI summary
@csrf_exempt
def save_edited_summary(request):
    if request.method == 'POST':
        filename = request.POST.get('filename')  # e.g., '20250504_200922'
        content = request.POST.get('content')    # the edited text
        
        base_name, _ = os.path.splitext(filename)
        
        if filename.endswith('_ai_summary.txt'):
            save_path = os.path.join(settings.MEDIA_ROOT, 'uploads', f'{filename}')
        else:
            save_path = os.path.join(settings.MEDIA_ROOT, 'uploads', f'{base_name}_ai_summary.txt')

        nice_url = base_name + '.txt'

        print(f'BASE NAME // {base_name}')
        print(f'NICE URL // {nice_url}')
        print(f'SAVE PATH // {save_path}')
        print(f'CONTENT // {content}')
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        #messages.success(request, f'You have been save this file!')
        #return redirect('ai_summary', nice_url)
        return HttpResponse('<div style="color: green; font-weight: bold;">You have successfully uploaded your file!</div>')
        #return JsonResponse({'status': 'success', 'path': save_path})
    return JsonResponse({'status': 'error'}, status=400) 

# NOTE JUST VIEW AI SUMMARY
def ai_summary(request, filename):
       
    path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)

    with open(path, 'r', encoding='utf-8') as f:
        ai_summary_text = f.read()

    return render(request, 'studio/ai_summary.html', {"filename":filename,"ai_summary_text":ai_summary_text})


# NOTE START WITH WeasyPrint PDF
def generate_pdf(request, layout_id, filename):

    path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)

    # GET DATE TIME
    current_date = datetime.datetime.now()

    with open(path, 'r', encoding='utf-8') as f:
        ai_summary_text = f.read()


    if layout_id == 1:
        html_string = render_to_string("studio/pdf_template.html",
                                   {"data": ai_summary_text,
                                    "date": current_date}
                                   )
    if layout_id == 2:
        html_string = render_to_string("studio/pdf_template2.html",
                                   {"data": ai_summary_text,
                                   "date": current_date}
                                   )
    if layout_id == 3:
        html_string = render_to_string("studio/pdf_template3.html",
                                   {"data": ai_summary_text,
                                   "date": current_date}
                                   )

    html = HTML(string=html_string)
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type="application/pdf")
    response['Content-Disposition'] = 'inline; filename="output.pdf"'
    return response 