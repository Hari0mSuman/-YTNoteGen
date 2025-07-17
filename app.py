from yt_dlp import YoutubeDL
import whisper
from transformers import pipeline
import os
import warnings
from pydub import AudioSegment
from pydub.utils import which
import tkinter as tk
from tkinter import messagebox, filedialog

warnings.filterwarnings("ignore", category=UserWarning)

def download_audio(url):
    base_path = r'C:\Users\h6354\OneDrive\Desktop\project\YTNoteGen'
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

def save_to_txt(text, filename="notes.txt"):
    save_path = os.path.join(
        r"C:\Users\h6354\OneDrive\Desktop\project\YTNoteGen", filename
    )
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(text)
    return save_path

def run_pipeline(url, status_label):
    try:
        status_label.config(text="🔊 Downloading audio...")
        audio_path = download_audio(url)
        status_label.config(text="📝 Transcribing audio...")
        transcript = transcribe_audio(audio_path)
        status_label.config(text="🧠 Summarizing transcript...")
        summary = summarize_text(transcript)
        status_label.config(text="💾 Saving notes...")
        save_path = save_to_txt(summary)
        status_label.config(text=f"✅ Done! Notes saved to {save_path}")
        messagebox.showinfo("Success", f"Your notes are ready in:\n{save_path}")
    except Exception as e:
        status_label.config(text="❌ Error occurred!")
        messagebox.showerror("Error", str(e))

def start_gui():
    root = tk.Tk()
    root.title("YTNoteGen - YouTube to Text Notes Generator")
    root.geometry("500x220")

    tk.Label(root, text="Enter YouTube video URL:").pack(pady=10)
    url_entry = tk.Entry(root, width=60)
    url_entry.pack(pady=5)

    status_label = tk.Label(root, text="", fg="blue")
    status_label.pack(pady=10)

    def on_generate():
        url = url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please provide a valid YouTube URL.")
            return
        root.after(100, lambda: run_pipeline(url, status_label))

    generate_btn = tk.Button(root, text="Generate Notes", command=on_generate)
    generate_btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    start_gui()