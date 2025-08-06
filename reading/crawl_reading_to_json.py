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

    # Click nút "Dịch tiếng Việt" để lấy nội dung dịch
    try:
        btn_translate = await page.query_selector('#toggleTranslationBtn')
        if btn_translate:
            await btn_translate.click()
            await asyncio.sleep(1)  # Đợi offcanvas mở ra
        dich_viet = await page.inner_text('#offcanvasTranslation .offcanvas-body')
        # Đóng popup dịch tiếng Việt bằng cách click nút đóng
        btn_close = await page.query_selector('#offcanvasTranslation .btn-close')
        if btn_close:
            await btn_close.click()
            await asyncio.sleep(0.5)  # Đợi popup đóng
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
        # Chỉ xử lý dialog một lần khi click submit
        async def handle_dialog(dialog):
            await dialog.accept()
        btn_submit = await page.query_selector('#btn-submit')
        if btn_submit:
            page.once("dialog", handle_dialog)
            await btn_submit.click()
            # Chờ đến khi đáp án xuất hiện (tối đa 5s)
            try:
                await page.wait_for_selector('.alert.alert-info', timeout=5000)
            except:
                await asyncio.sleep(3)  # Nếu không xuất hiện, vẫn chờ thêm
        # Lưu lại HTML của trang sau khi nộp bài để phân tích
        html_after_submit = await page.content()
        with open(f"reading/debug_reading_{idx}.html", "w", encoding="utf-8") as f:
            f.write(html_after_submit)
        # Sau khi nộp bài, lấy giải thích/đáp án cho từng câu hỏi
        answer_blocks = await page.query_selector_all('.question-block')
        for ab in answer_blocks:
            try:
                # Đáp án đúng
                correct_span = await ab.query_selector('span.text-success')
                correct_answer = await correct_span.inner_text() if correct_span else None
                # Giải thích chi tiết
                explanation_div = await ab.query_selector('div.mt-4')
                explanation_html = await explanation_div.inner_text() if explanation_div else None
                answers.append({
                    "answer": correct_answer,
                    "explanation": explanation_html
                })
            except:
                answers.append({"answer": None, "explanation": None})
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
        for i in range(1, 49):
            print(f"Extracting reading {i}")
            data = await extract_reading_info(page, i)
            all_data.append(data)
        with open("reading/reading_output.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
