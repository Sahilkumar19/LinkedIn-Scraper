from browser_use import Browser, BrowserConfig, BrowserContextConfig
from pathlib import Path

class PersistentBrowser:
    def __init__(self, profile_name="default"):
        self.cache_dir = Path(f".browser_cache/{profile_name}")
        self.config = BrowserConfig(
            chrome_instance_path="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",  # Use existing Chrome
            new_context_config=BrowserContextConfig(
                cookies_file=str(self.cache_dir/"cookies.json"),
                save_recording_path=str(self.cache_dir/"recordings"),
                trace_path=str(self.cache_dir/"traces"),
                browser_window_size={'width': 1280, 'height': 1100},
                highlight_elements=False,  # Disable for faster execution
                viewport_expansion=100  # Reduce context window size
            )
        )
        self.browser = Browser(config=self.config)

    async def get_context(self):
        return await self.browser.new_context(
            config=BrowserContextConfig(
                allowed_domains=['linkedin.com'],  # Restrict to target site
                locale='en-US',
                user_agent='Mozilla/5.0...'  # Consistent UA for caching
            )
        )