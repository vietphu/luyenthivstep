import asyncio
from playwright.async_api import async_playwright
import os

OUTPUT_DIR = os.path.dirname(__file__)

USERNAME = "VSTEP203118"
PASSWORD = "541287"

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

        for idx in range(1, 8):
            url = f'https://luyenthivstep.vn/practice/speaking/{idx}'
            await page.goto(url)
            await page.wait_for_load_state('networkidle')
            out_path = os.path.join(OUTPUT_DIR, f'speaking_{idx}.html')
            html = await page.content()
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f'Saved: {out_path}')
        await browser.close()

if __name__ == "__main__":
    asyncio.run(crawl_speaking())
