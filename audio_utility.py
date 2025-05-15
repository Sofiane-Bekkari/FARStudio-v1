import os
import django

from django.conf import settings
import whisper

# Set the environment variable to point to your settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "farstudio.settings")  # Change to your actual project settings

# Initialize Django
django.setup()

def whisper_transcript_audio(filename):    
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

    return transcription_text


# NOTE TEST AND RUN
# tran_audio('20250504_201022.webm')

# TRYING TO RETRIVE DURATION FOR AUDIO
import subprocess
import json

def get_duration_ffprobe(filename):
    file_path = 'media/uploads/' + filename
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                file_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # decode to string
        )
        output = result.stdout
        data = json.loads(output)
        if "format" in data and "duration" in data["format"]:
            return round(float(data["format"]["duration"]), 2)
        else:
            print("Duration not found in metadata.")
            return None
    except json.JSONDecodeError as je:
        print("JSON decode error:", je)
        print("ffprobe output:", result.stdout)
    except Exception as e:
        print("General error:", e)
    return None

# Example usage
#duration = get_duration_ffprobe("20250514_143222.webm")
#print("Duration:", duration, "seconds")

