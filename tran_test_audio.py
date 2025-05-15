import os
import django

from django.conf import settings
import whisper

# Set the environment variable to point to your settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "farstudio.settings")  # Change to your actual project settings

# Initialize Django
#django.setup()

def tran_audio(filename):    
    audio_path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)

    if not os.path.exists(audio_path):
        return print({'status': 'error', 'message': 'Audio file not found'}, status=404)

    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    transcription_text = result['text']

    # Save the transcription as a text file
    base_name, _ = os.path.splitext(filename)
    transcript_filename = base_name + ".txt"
    transcript_path = os.path.join(settings.MEDIA_ROOT, 'uploads', transcript_filename)

    with open(transcript_path, 'w', encoding='utf-8') as f:
        f.write(transcription_text)

    transcription_url = f"{settings.MEDIA_URL}uploads/{transcript_filename}"

    print(f'Done transcript file: {transcription_url}')
    print(f'Done transcript text: {transcription_text}')

    return transcription_url


# NOTE TEST AND RUN
tran_audio('20250515_105750.webm')