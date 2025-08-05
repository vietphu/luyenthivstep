
import asyncio
import json
from playwright.async_api import async_playwright
import os

RESULT_DIR = "listening/result_html"
os.makedirs(RESULT_DIR, exist_ok=True)

USERNAME = "VSTEP203118"
PASSWORD = "541287"

async def crawl_listening():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        # Đăng nhập
        await page.goto("https://luyenthivstep.vn/user/login")
        await page.fill('input[name="user_name"]', USERNAME)
        await page.fill('input[name="password"]', PASSWORD)
        await page.click('button[type="submit"]')
        await page.wait_for_load_state('networkidle')

        data = []
        for i in range(1, 2):
            url = f"https://luyenthivstep.vn/practice/listening/{i}"
            print(f"Đang crawl đề nghe số {i}: {url}")
            await page.goto(url)
            await page.wait_for_load_state('networkidle')

            # Lấy thông tin đề nghe trước khi nộp bài
            page_content = await page.content()
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(page_content, "html.parser")
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
                        with open(os.path.join("listening/audio", audio_filename), "wb") as af:
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


            # Click nút 'Nộp bài' và xử lý dialog xác nhận
            try:
                async def handle_dialog(dialog):
                    await dialog.accept()
                submit_button = await page.query_selector("button:has-text('Nộp bài')")
                if submit_button:
                    page.once("dialog", handle_dialog)
                    await submit_button.click()
                    # Chờ trang đáp án hiện ra (tối đa 5s)
                    try:
                        await page.wait_for_selector('.alert.alert-info', timeout=5000)
                    except:
                        await asyncio.sleep(2)
                else:
                    print(f"Không tìm thấy nút 'Nộp bài' ở {url}")
            except Exception as e:
                print(f"Playwright error for {url}: {e}")
            # Lưu HTML kết quả
            result_html_path = os.path.join(RESULT_DIR, f"listening_{i}_result.html")
            html_result = await page.content()
            with open(result_html_path, "w", encoding="utf-8") as rf:
                rf.write(html_result)

            # Phân tích đáp án và giải thích từ HTML kết quả
            from bs4 import BeautifulSoup
            soup_result = BeautifulSoup(html_result, "html.parser")
            result_blocks = soup_result.find_all("div", class_="question-block")
            question_outputs = []
            for idx, q in enumerate(questions):
                answer_text = None
                explanation = None
                if idx < len(result_blocks):
                    block = result_blocks[idx]
                    # Đáp án: lấy span.text-success trong block
                    ans_span = block.find("span", class_="text-success")
                    if ans_span:
                        answer_text = ans_span.get_text(strip=True)
                    # Giải thích: tìm p chứa "Giải thích chi tiết" trong block
                    explain_p = block.find("p", string=lambda s: s and "Giải thích chi tiết" in s)
                    if explain_p:
                        explanation_parts = []
                        next_sibling = explain_p.find_next_sibling()
                        while next_sibling and next_sibling.name == "p" and "Giải thích chi tiết" not in next_sibling.get_text():
                            explanation_parts.append(next_sibling.get_text(strip=True))
                            next_sibling = next_sibling.find_next_sibling()
                        explanation = "\n".join(explanation_parts)
                question_outputs.append({
                    "question": q["question"],
                    "choices": q["choices"],
                    "answer": answer_text,
                    "explanation": explanation
                })

            data.append({
                "id": i,
                "audio_file": audio_filename,
                "audio_url": audio_src,
                "transcript": transcript,
                "translation": translation,
                "questions": question_outputs
            })

            # Click nút 'Nộp bài' và xử lý dialog xác nhận
            try:
                async def handle_dialog(dialog):
                    await dialog.accept()
                submit_button = await page.query_selector("button:has-text('Nộp bài')")
                if submit_button:
                    page.once("dialog", handle_dialog)
                    await submit_button.click()
                    # Chờ trang đáp án hiện ra (tối đa 5s)
                    try:
                        await page.wait_for_selector('.alert.alert-info', timeout=5000)
                    except:
                        await asyncio.sleep(2)
                else:
                    print(f"Không tìm thấy nút 'Nộp bài' ở {url}")
            except Exception as e:
                print(f"Playwright error for {url}: {e}")
            # Lưu HTML kết quả
            result_html_path = os.path.join(RESULT_DIR, f"listening_{i}_result.html")
            with open(result_html_path, "w", encoding="utf-8") as rf:
                rf.write(await page.content())
        # Lưu dữ liệu đề nghe ra file json
        with open("listening/listening_output.json", "w", encoding="utf-8") as jf:
            json.dump(data, jf, ensure_ascii=False, indent=2)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(crawl_listening())
