import random
import time
import logging
from typing import Optional

from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

_ua = UserAgent()


def random_user_agent() -> str:
    try:
        return _ua.random
    except Exception:
        return (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )


def random_delay(min_s: float = 2.0, max_s: float = 5.0) -> None:
    delay = random.uniform(min_s, max_s)
    logger.debug("Sleeping %.2fs", delay)
    time.sleep(delay)


def build_session(proxy_url: Optional[str] = None):
    """Return a requests.Session pre-configured with headers and optional proxy."""
    import requests

    session = requests.Session()
    session.headers.update({
        "User-Agent": random_user_agent(),
        "Accept-Language": "pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "DNT": "1",
    })
    if proxy_url:
        session.proxies = {"http": proxy_url, "https": proxy_url}
    return session


def build_selenium_driver(headless: bool = True, proxy_url: Optional[str] = None):
    """Return an undetected Chrome WebDriver."""
    try:
        import undetected_chromedriver as uc
        from selenium.webdriver.chrome.options import Options

        options = uc.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(f"--user-agent={random_user_agent()}")
        if proxy_url:
            options.add_argument(f"--proxy-server={proxy_url}")

        driver = uc.Chrome(options=options)
        driver.implicitly_wait(10)
        return driver
    except Exception as exc:
        logger.error("Could not start Chrome driver: %s", exc)
        raise
