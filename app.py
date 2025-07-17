from yt_dlp import YoutubeDL
import whisper
from transformers import pipeline
import os
from pydub import AudioSegment
from pydub.utils import which
from flask import Flask, request, render_template_string

app = Flask(__name__)

def download_audio(url):
    base_path = os.path.dirname(os.path.abspath(__file__))
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio',
        'outtmpl': os.path.join(base_path, 'audio.%(ext)s'),
        'quiet': True
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        audio_path = ydl.prepare_filename(info_dict)
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Downloaded audio file not found: {audio_path}")
        if not which("ffmpeg"):
            raise EnvironmentError("FFmpeg not found. Make sure it's installed and added to your PATH.")
        wav_path = os.path.join(base_path, "audio.wav")
        AudioSegment.from_file(audio_path).export(wav_path, format="wav")
        if not os.path.exists(wav_path):
            raise FileNotFoundError(f"WAV file not created: {wav_path}")
        return wav_path

def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

def summarize_text(text):
    summarizer = pipeline("summarization")
    chunks = [text[i:i + 1000] for i in range(0, len(text), 1000)]
    summary = ""
    for chunk in chunks:
        result = summarizer(chunk, max_length=130, min_length=30, do_sample=False)
        summary += result[0]['summary_text'].strip() + "\n"
    return summary.strip()

@app.route("/", methods=["GET", "POST"])
def index():
    notes = ""
    error = ""
    if request.method == "POST":
        url = request.form.get("url", "").strip()
        if not url:
            error = "Please provide a valid YouTube URL."
        else:
            try:
                audio_path = download_audio(url)
                transcript = transcribe_audio(audio_path)
                notes = summarize_text(transcript)
            except Exception as e:
                error = str(e)
    return render_template_string("""
        <h2>YouTube to Notes Generator</h2>
        <form method="post">
            <input name="url" style="width:400px" placeholder="YouTube URL">
            <button type="submit">Generate Notes</button>
        </form>
        {% if notes %}
            <h3>Notes:</h3>
            <pre>{{ notes }}</pre>
        {% endif %}
        {% if error %}
            <p style="color:red;">{{ error }}</p>
        {% endif %}
    """, notes=notes, error=error)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
