import asyncio
import json
from playwright.async_api import async_playwright

async def extract_reading_info(page, idx):
    url = f"https://luyenthivstep.vn/practice/reading/{idx}"
    await page.goto(url)
    await page.wait_for_load_state('networkidle')
    # Bài đọc (đề bài)
    try:
        reading_card = await page.query_selector('div.col-md-6.mb-4 .card-body')
        reading_paragraphs = await reading_card.query_selector_all('p')
        reading_text = '\n'.join([await p.inner_text() for p in reading_paragraphs])
    except:
        reading_text = None
    # Dịch tiếng Việt
    try:
        dich_viet = await page.inner_text('#offcanvasTranslation .offcanvas-body')
    except:
        dich_viet = None
    # Danh sách câu hỏi
    questions = []
    question_blocks = await page.query_selector_all('.question-block')
    for qb in question_blocks:
        try:
            q_title = await qb.query_selector('div.fw-bold')
            q_text = await q_title.inner_text() if q_title else ""
            choices = []
            choice_labels = await qb.query_selector_all('.form-check-label')
            for cl in choice_labels:
                choices.append(await cl.inner_text())
            questions.append({
                "question": q_text,
                "choices": choices
            })
        except:
            continue
    # Click "Nộp bài" để lấy đáp án và giải thích
    answers = []
    try:
        submit_btn = await page.query_selector('form#submitForm button[type="submit"]')
        if submit_btn:
            await submit_btn.click()
            await page.wait_for_load_state('networkidle')
            # Giải thích/đáp án sau khi nộp bài
            answer_blocks = await page.query_selector_all('.question-block')
            for ab in answer_blocks:
                try:
                    explanation = await ab.query_selector('.alert.alert-info')
                    answer_text = await explanation.inner_text() if explanation else None
                    answers.append({"explanation": answer_text})
                except:
                    answers.append({"explanation": None})
    except:
        answers = []
    return {
        "index": idx,
        "reading_text": reading_text,
        "questions": questions,
        "dich_tieng_viet": dich_viet,
        "answers": answers
    }

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://luyenthivstep.vn/user/login")
        await page.fill('input[name="user_name"]', "VSTEP203118")
        await page.fill('input[name="password"]', "541287")
        await page.click('button[type="submit"]')
        await page.wait_for_load_state('networkidle')
        all_data = []
        for i in range(1, 10):
            print(f"Extracting reading {i}")
            data = await extract_reading_info(page, i)
            all_data.append(data)
        with open("reading/reading_output.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
