
import asyncio
import json
from playwright.async_api import async_playwright

async def extract_writing(page, idx):
    url = f"https://luyenthivstep.vn/practice/writing/{idx}"
    await page.goto(url)
    await page.wait_for_load_state('networkidle')

    # Lấy đề bài tiếng Anh
    prompt_en = await page.eval_on_selector(
        ".card-body .mb-3.bg-light.border.rounded.p-3", "el => el.innerText"
    )

    # Click nút dịch tiếng Việt
    await page.click("#toggleTranslationBtn")
    await page.wait_for_selector("#offcanvasTranslation.show", timeout=3000)
    prompt_vi = await page.eval_on_selector(
        "#offcanvasTranslation .offcanvas-body", "el => el.innerText"
    )

    # Trích xuất thông tin meta
    min_words = 120
    task = "Write a letter to respond to Brianna."
    criteria = ["Task Fulfillment", "Organization", "Vocabulary", "Grammar"]

    return {
        "id": idx,
        "title": f"Writing VSTEP - Đề {idx}",
        "prompt_en": prompt_en,
        "prompt_vi": prompt_vi,
        "meta": {
            "min_words": min_words,
            "task": task,
            "criteria": criteria
        }
    }

async def crawl_writing():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        # Đăng nhập
        await page.goto("https://luyenthivstep.vn/user/login")
        await page.fill('input[name="user_name"]', "VSTEP203118")
        await page.fill('input[name="password"]', "541287")
        await page.click('button[type="submit"]')
        await page.wait_for_load_state('networkidle')

        results = []
        for i in range(1, 4):
            print(f"Đang crawl đề writing số {i}")
            data = await extract_writing(page, i)
            results.append(data)

        # Lưu ra file JSON
        with open("writing/writing_prompts.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print("Đã lưu writing/writing_prompts.json")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(crawl_writing())
