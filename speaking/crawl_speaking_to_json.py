import asyncio
import json
from playwright.async_api import async_playwright
import os

OUTPUT_DIR = os.path.dirname(__file__)
USERNAME = "VSTEP203118"
PASSWORD = "541287"

async def extract_speaking(page, idx):
    url = f"https://luyenthivstep.vn/practice/speaking/{idx}"
    await page.goto(url)
    await page.wait_for_load_state('networkidle')

    # Lấy phân loại part
    part_text = await page.eval_on_selector(
        '.bg-white.border-bottom.shadow-sm.sticky-top.z-1.px-3.py-2 .container-fluid .row .col-12.col-md-6.text-center span.fw-bold.text-muted.small.d-block',
        'el => el.innerText'
    )
    part = None
    if part_text:
        if 'Part 1' in part_text:
            part = 1
        elif 'Part 2' in part_text:
            part = 2
        elif 'Part 3' in part_text:
            part = 3

    # Lấy thời gian thực hiện
    time_limit = await page.eval_on_selector(
        '.d-flex.justify-content-between.align-items-center.fw-bold.my-4 span.text-primary',
        'el => el.innerText'
    )

    # Lấy nội dung đề thi tiếng Anh
    prompt_en = await page.eval_on_selector(
        '.bg-light.rounded.p-3.border.mb-3', 'el => el.innerText'
    )

    # Click nút dịch tiếng Việt
    await page.click('#toggleTranslationBtn')
    await page.wait_for_selector('#offcanvasTranslation.show', timeout=3000)
    prompt_vi = await page.eval_on_selector(
        '#offcanvasTranslation .offcanvas-body', 'el => el.innerText'
    )

    # Nếu là Part 3, trích xuất sơ đồ ý tưởng và follow-up questions
    idea_map = None
    follow_up_questions_en = None
    follow_up_questions_vi = None
    if part == 3:
        # Sơ đồ ý tưởng tiếng Anh
        # Tìm các node ý tưởng trong sơ đồ
        idea_nodes = await page.query_selector_all('.khoa-con')
        main_node = await page.query_selector('.khoa-cha')
        idea_map = {
            "main": await main_node.inner_text() if main_node else None,
            "branches": [await node.inner_text() for node in idea_nodes] if idea_nodes else []
        }

        # Follow-up questions tiếng Anh
        # Tìm trong prompt_en, tách các câu hỏi follow-up
        if prompt_en:
            followup_split = prompt_en.split('Follow-up questions:')
            if len(followup_split) > 1:
                follow_up_questions_en = [q.strip() for q in followup_split[1].split('\n') if q.strip()]
        # Follow-up questions tiếng Việt
        if prompt_vi:
            followup_split_vi = prompt_vi.split('Câu hỏi gợi ý:')
            if len(followup_split_vi) > 1:
                follow_up_questions_vi = [q.strip() for q in followup_split_vi[1].split('\n') if q.strip()]

    result = {
        "id": idx,
        "part": part,
        "time_limit": time_limit,
        "prompt_en": prompt_en,
        "prompt_vi": prompt_vi
    }
    if part == 3:
        result["idea_map"] = idea_map
        result["follow_up_questions_en"] = follow_up_questions_en
        result["follow_up_questions_vi"] = follow_up_questions_vi
    return result

async def crawl_speaking():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        # Đăng nhập
        await page.goto("https://luyenthivstep.vn/user/login")
        await page.fill('input[name="user_name"]', USERNAME)
        await page.fill('input[name="password"]', PASSWORD)
        await page.click('button[type="submit"]')
        await page.wait_for_load_state('networkidle')

        results = []
        for i in range(1, 8):
            print(f"Đang crawl đề speaking số {i}")
            data = await extract_speaking(page, i)
            results.append(data)

        # Lưu ra file JSON
        out_path = os.path.join(OUTPUT_DIR, "speaking_prompts.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Đã lưu {out_path}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(crawl_speaking())
