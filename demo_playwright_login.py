
import asyncio
from playwright.async_api import async_playwright

async def crawl_listening(page):
    print("\n--- Luyện đề nghe (/practice/listening) ---")
    await page.goto("https://luyenthivstep.vn/practice/listening")
    await page.wait_for_load_state('networkidle')
    content = await page.content()
    with open("listening/listening.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("Đã lưu listening/listening.html")

    # Chỉ crawl nội dung từ bài nghe số 1 đến số 9
    for i in range(1, 10):
        url = f"https://luyenthivstep.vn/practice/listening/{i}"
        print(f"\n--- Đang crawl bài nghe số {i}: {url} ---")
        await page.goto(url)
        await page.wait_for_load_state('networkidle')
        detail_content = await page.content()
        with open(f"listening/listening_{i}.html", "w", encoding="utf-8") as f:
            f.write(detail_content)
        print(f"Đã lưu listening/listening_{i}.html")

async def crawl_reading(page):
    print("\n--- Luyện đề đọc (/practice/reading) ---")
    await page.goto("https://luyenthivstep.vn/practice/reading")
    await page.wait_for_load_state('networkidle')
    content = await page.content()
    with open("reading.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("Đã lưu reading.html")

async def crawl_writing(page):
    print("\n--- Luyện đề viết (/practice/writing) ---")
    await page.goto("https://luyenthivstep.vn/practice/writing")
    await page.wait_for_load_state('networkidle')
    content = await page.content()
    with open("writing.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("Đã lưu writing.html")

async def crawl_speaking(page):
    print("\n--- Luyện đề nói (/practice/speaking) ---")
    await page.goto("https://luyenthivstep.vn/practice/speaking")
    await page.wait_for_load_state('networkidle')
    content = await page.content()
    with open("speaking.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("Đã lưu speaking.html")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        # Go to login page
        await page.goto("https://luyenthivstep.vn/user/login")
        # Fill in login form
        await page.fill('input[name="user_name"]', "VSTEP203118")
        await page.fill('input[name="password"]', "541287")
        await page.click('button[type="submit"]')
        # Wait for navigation after login
        await page.wait_for_load_state('networkidle')
        # Lấy tất cả menu và link trên trang sau đăng nhập
        menu_items = await page.query_selector_all('nav a, .navbar a, .sidebar a')
        print("Menu items and links after login:")
        for item in menu_items:
            text = await item.inner_text()
            href = await item.get_attribute('href')
            print(f"{text}: {href}")
        # Gọi từng hàm crawler cho từng phần
        await crawl_listening(page)
        await crawl_reading(page)
        await crawl_writing(page)
        await crawl_speaking(page)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
