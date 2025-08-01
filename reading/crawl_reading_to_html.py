import asyncio
from playwright.async_api import async_playwright

async def crawl_reading_pages():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        # Go to login page
        await page.goto("https://luyenthivstep.vn/user/login")
        await page.fill('input[name="user_name"]', "VSTEP203118")
        await page.fill('input[name="password"]', "541287")
        await page.click('button[type="submit"]')
        await page.wait_for_load_state('networkidle')
        # Crawl reading pages 1-9
        for i in range(1, 10):
            url = f"https://luyenthivstep.vn/practice/reading/{i}"
            print(f"Crawling: {url}")
            await page.goto(url)
            await page.wait_for_load_state('networkidle')
            content = await page.content()
            with open(f"reading/reading_{i}.html", "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Saved reading/reading_{i}.html")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(crawl_reading_pages())
