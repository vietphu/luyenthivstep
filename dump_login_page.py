import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        # Go to login page
        await page.goto("https://luyenthivstep.vn/user/login")
        # Output login page HTML for inspection
        with open("login_page.html", "w", encoding="utf-8") as f:
            f.write(await page.content())
        print("Login page HTML saved to login_page.html")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
