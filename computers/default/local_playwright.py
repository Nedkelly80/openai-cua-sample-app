from playwright.sync_api import Browser, Page
from ..shared.base_playwright import BasePlaywrightComputer


class LocalPlaywrightBrowser(BasePlaywrightComputer):
    """Launches a local Chromium instance using Playwright."""

    def __init__(self, headless: bool = False):
        super().__init__()
        self.headless = headless

    def _get_browser_and_page(self) -> tuple[Browser, Page]:
        width, height = self.get_dimensions()
        launch_args = [
            f"--window-size={width},{height}",
            "--disable-extensions",
            "--disable-file-system",
        ]
        
        try:
            browser = self._playwright.chromium.launch(
                chromium_sandbox=True,
                headless=self.headless,
                args=launch_args,
                env={"DISPLAY": ":0"},
            )
        except Exception as e:
            print(f"Failed to launch browser: {e}")
            print("This might be due to missing dependencies. Try running: playwright install chromium")
            raise

        try:
            context = browser.new_context()

            # Add event listeners for page creation and closure
            context.on("page", self._handle_new_page)

            page = context.new_page()
            page.set_viewport_size({"width": width, "height": height})
            page.on("close", self._handle_page_close)

            # Try to navigate to initial page with retry
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    page.goto("https://bing.com", wait_until="domcontentloaded", timeout=10000)
                    break
                except Exception as nav_error:
                    if attempt == max_retries - 1:
                        print(f"Failed to navigate to initial page after {max_retries} attempts: {nav_error}")
                        # Continue without initial navigation rather than failing completely
                    else:
                        print(f"Navigation attempt {attempt + 1} failed, retrying...")

            return browser, page
        except Exception as e:
            browser.close()
            raise

    def _handle_new_page(self, page: Page):
        """Handle the creation of a new page."""
        print("New page created")
        self._page = page
        page.on("close", self._handle_page_close)

    def _handle_page_close(self, page: Page):
        """Handle the closure of a page."""
        print("Page closed")
        if self._page == page:
            if self._browser.contexts[0].pages:
                self._page = self._browser.contexts[0].pages[-1]
            else:
                print("Warning: All pages have been closed.")
                self._page = None
