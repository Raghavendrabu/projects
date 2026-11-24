import asyncio
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from config import BROWSER_STORAGE_DIR, SCREENSHOTS_DIR

class BrowserDriver:
    """
    Playwright-powered Browser Automation Engine with persistent session storage & screenshot capability.
    """

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def initialize(self):
        if not self.playwright:
            self.playwright = await async_playwright().start()
            # Launch context with persistent storage so user stays logged in across sessions
            user_data_dir = BROWSER_STORAGE_DIR / "user_profile"
            user_data_dir.mkdir(exist_ok=True)

            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(user_data_dir),
                headless=self.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized"
                ],
                viewport={"width": 1280, "height": 800}
            )
            if self.context.pages:
                self.page = self.context.pages[0]
            else:
                self.page = await self.context.new_page()

    async def open_url(self, url: str) -> Dict[str, Any]:
        await self.initialize()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        print(f"[Browser] Navigating to: {url}")
        response = await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
        title = await self.page.title()
        screenshot_path = await self.take_screenshot("open_url")
        return {
            "status": "success",
            "url": self.page.url,
            "title": title,
            "screenshot": screenshot_path
        }

    async def fill_and_submit_login(self, username_selector: str, password_selector: str, submit_selector: str, username: str, secret: str) -> Dict[str, Any]:
        await self.initialize()
        print(f"[Browser] Performing automated login...")
        if username_selector and username:
            await self.page.fill(username_selector, username)
        if password_selector and secret:
            await self.page.fill(password_selector, secret)
        
        if submit_selector:
            await self.page.click(submit_selector)
            await self.page.wait_for_timeout(3000)
        
        screenshot_path = await self.take_screenshot("login_result")
        return {
            "status": "success",
            "current_url": self.page.url,
            "title": await self.page.title(),
            "screenshot": screenshot_path
        }

    async def auto_login_service(self, service_name: str, target_url: str, username: str, secret: str) -> Dict[str, Any]:
        await self.open_url(target_url)
        await self.page.wait_for_timeout(2000)

        # Smart selector guessing for common logins
        username_selectors = ['input[type="email"]', 'input[name="username"]', 'input[name="email"]', 'input[type="text"]', '#username', '#email']
        password_selectors = ['input[type="password"]', 'input[name="password"]', '#password']
        submit_selectors = ['button[type="submit"]', 'input[type="submit"]', 'button:has-text("Sign in")', 'button:has-text("Log in")', 'button:has-text("Login")']

        u_sel = None
        for sel in username_selectors:
            if await self.page.query_selector(sel):
                u_sel = sel
                break
        
        p_sel = None
        for sel in password_selectors:
            if await self.page.query_selector(sel):
                p_sel = sel
                break

        s_sel = None
        for sel in submit_selectors:
            if await self.page.query_selector(sel):
                s_sel = sel
                break

        if u_sel and p_sel:
            return await self.fill_and_submit_login(u_sel, p_sel, s_sel, username, secret)
        else:
            screenshot_path = await self.take_screenshot("login_selectors_missing")
            return {
                "status": "warning",
                "message": f"Could not automatically detect login inputs on {target_url}. Loaded page for manual login.",
                "screenshot": screenshot_path
            }

    async def click_element(self, selector: str) -> Dict[str, Any]:
        await self.initialize()
        await self.page.click(selector)
        await self.page.wait_for_timeout(1000)
        screenshot_path = await self.take_screenshot("click_element")
        return {"status": "success", "action": "click", "selector": selector, "screenshot": screenshot_path}

    async def type_text(self, selector: str, text: str) -> Dict[str, Any]:
        await self.initialize()
        await self.page.fill(selector, text)
        screenshot_path = await self.take_screenshot("type_text")
        return {"status": "success", "action": "type", "text": text, "screenshot": screenshot_path}

    async def take_screenshot(self, name_prefix: str = "shot") -> str:
        if not self.page:
            return ""
        timestamp = int(time.time() * 1000)
        filename = f"{name_prefix}_{timestamp}.png"
        filepath = SCREENSHOTS_DIR / filename
        await self.page.screenshot(path=str(filepath))
        # Keep relative path for web serving
        return f"/screenshots/{filename}"

    async def close(self):
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()
        self.context = None
        self.playwright = None
        self.page = None
