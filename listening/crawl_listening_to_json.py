import os
import json
from bs4 import BeautifulSoup

INPUT_DIR = "listening"
OUTPUT_DIR = "listening/audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Crawl 9 listening files
data = []
for i in range(1, 10):
    html_path = os.path.join(INPUT_DIR, f"listening_{i}.html")
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Audio file
    audio_tag = soup.find("audio")
    audio_src = None
    audio_filename = None
    if audio_tag and audio_tag.find("source"):
        audio_src = audio_tag.find("source").get("src")
        if audio_src:
            audio_url = f"https://luyenthivstep.vn{audio_src}" if audio_src.startswith("/") else audio_src
            audio_filename = f"audio_{i}.mp3"
            # Download audio file
            try:
                import requests
                r = requests.get(audio_url)
                with open(os.path.join(OUTPUT_DIR, audio_filename), "wb") as af:
                    af.write(r.content)
            except Exception as e:
                print(f"Error downloading audio for listening {i}: {e}")

    # Transcript
    transcript = None
    transcript_div = soup.find("div", id="offcanvasTranscript")
    if transcript_div:
        transcript_body = transcript_div.find("div", class_="offcanvas-body")
        if transcript_body:
            transcript = transcript_body.get_text(strip=True, separator="\n")

    # Translation
    translation = None
    translation_div = soup.find("div", id="offcanvasTranslation")
    if translation_div:
        translation_body = translation_div.find("div", class_="offcanvas-body")
        if translation_body:
            translation = translation_body.get_text(strip=True, separator="\n")

    # Questions
    questions = []
    for qdiv in soup.find_all("div", class_="question-block"):
        qtext = qdiv.find("div", class_="fw-bold")
        question = qtext.get_text(strip=True) if qtext else None
        choices = []
        for label in qdiv.find_all("label", class_="form-check-label"):
            choices.append(label.get_text(strip=True))
        questions.append({"question": question, "choices": choices})

    data.append({
        "id": i,
        "audio_file": audio_filename,
        "audio_url": audio_src,
        "transcript": transcript,
        "translation": translation,
        "questions": questions
    })

with open(os.path.join(INPUT_DIR, "listening_output.json"), "w", encoding="utf-8") as jf:
    json.dump(data, jf, ensure_ascii=False, indent=2)
print("Đã lưu listening_output.json và các file audio.")
