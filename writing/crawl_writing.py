
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
    import random
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        # Set user-agent giống Chrome thật
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        context = await browser.new_context(user_agent=user_agent)
        page = await context.new_page()
        # Đăng nhập
        await page.goto("https://luyenthivstep.vn/user/login")
        await page.fill('input[name="user_name"]', "VSTEP203118")
        await page.fill('input[name="password"]', "541287")
        await page.click('button[type="submit"]')
        await page.wait_for_load_state('networkidle')

        results = []
        for i in range(1, 75):
            print(f"Đang crawl đề writing số {i}")
            # Thêm delay ngẫu nhiên giữa các lần crawl
            await asyncio.sleep(random.uniform(2, 5))
            try:
                url = f"https://luyenthivstep.vn/practice/writing/{i}"
                await page.goto(url)
                await page.wait_for_load_state('networkidle')
                # Di chuyển chuột ngẫu nhiên trên trang để giả lập hành vi người dùng
                width = page.viewport_size['width'] if page.viewport_size else 1200
                height = page.viewport_size['height'] if page.viewport_size else 800
                for _ in range(random.randint(1, 3)):
                    x = random.randint(0, width-1)
                    y = random.randint(0, height-1)
                    await page.mouse.move(x, y)
            except Exception as e:
                print(f"[SKIP] Đề writing {i} - Lỗi truy cập trang: {e}")
                continue
            try:
                data = await extract_writing(page, i)
                results.append(data)
            except Exception as e:
                print(f"[SKIP] Đề writing {i} - Lỗi extract dữ liệu: {e}")
                continue

        # Lưu ra file JSON
        with open("writing/writing_prompts.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print("Đã lưu writing/writing_prompts.json")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(crawl_writing())
