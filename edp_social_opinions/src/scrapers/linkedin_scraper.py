"""
LinkedIn employee opinion scraper for EDP.

LinkedIn requires authentication to access company reviews and employee posts.
This scraper uses Selenium + undetected-chromedriver to:
  1. Log in with provided credentials.
  2. Navigate to the EDP company page and collect employee posts/recommendations.
  3. Navigate to the "Life" tab for employee-authored content.

Note: LinkedIn's Terms of Service restrict automated scraping.
      Use only with proper authorisation.
"""

import logging
import re
import time
from typing import List, Optional

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import COMPANY, CREDENTIALS, SCRAPER
from src.models.opinion import Opinion
from src.utils.browser_utils import build_selenium_driver, random_delay

logger = logging.getLogger(__name__)

LOGIN_URL = "https://www.linkedin.com/login"
COMPANY_REVIEWS_URL = (
    f"https://www.linkedin.com/company/{COMPANY['linkedin_company_id']}/life/"
)
COMPANY_POSTS_URL = (
    f"https://www.linkedin.com/company/{COMPANY['linkedin_company_id']}/posts/"
)
JOBS_REVIEWS_URL = (
    f"https://www.linkedin.com/company/{COMPANY['linkedin_company_id']}/jobs/"
)


class LinkedInScraper:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.max_posts = SCRAPER["max_pages"] * 10  # ~10 posts per scroll

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scrape(self) -> List[Opinion]:
        if not CREDENTIALS["linkedin_email"] or not CREDENTIALS["linkedin_password"]:
            logger.warning(
                "LinkedIn credentials not set. Skipping LinkedIn scraper. "
                "Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env"
            )
            return []

        opinions: List[Opinion] = []
        try:
            self.driver = build_selenium_driver(
                headless=SCRAPER["headless_browser"],
                proxy_url=SCRAPER.get("proxy_url"),
            )
            self.wait = WebDriverWait(self.driver, 20)

            if not self._login():
                logger.error("LinkedIn login failed.")
                return []

            opinions.extend(self._scrape_life_tab())
            opinions.extend(self._scrape_company_posts())

        except Exception as exc:
            logger.error("LinkedIn scraper error: %s", exc)
        finally:
            if self.driver:
                self.driver.quit()

        logger.info("LinkedIn: %d total opinions collected.", len(opinions))
        return opinions

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------

    def _login(self) -> bool:
        try:
            self.driver.get(LOGIN_URL)
            random_delay(2, 4)

            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.clear()
            email_field.send_keys(CREDENTIALS["linkedin_email"])

            pass_field = self.driver.find_element(By.ID, "password")
            pass_field.clear()
            pass_field.send_keys(CREDENTIALS["linkedin_password"])

            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            random_delay(3, 6)

            # Check for successful login by looking for nav or feed
            return "feed" in self.driver.current_url or "checkpoint" not in self.driver.current_url
        except Exception as exc:
            logger.error("Login step failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Life tab (employee stories, culture posts)
    # ------------------------------------------------------------------

    def _scrape_life_tab(self) -> List[Opinion]:
        opinions: List[Opinion] = []
        logger.info("LinkedIn: scraping Life tab")
        try:
            self.driver.get(COMPANY_REVIEWS_URL)
            random_delay(3, 5)
            self._scroll_page(scrolls=5)

            posts = self.driver.find_elements(
                By.CSS_SELECTOR, "div.org-life__employee-content-card"
            )
            if not posts:
                posts = self.driver.find_elements(
                    By.CSS_SELECTOR, "[data-finite-scroll-hotkey-item]"
                )

            for post in posts:
                opinion = self._extract_post_opinion(post, COMPANY_REVIEWS_URL)
                if opinion:
                    opinions.append(opinion)

        except Exception as exc:
            logger.warning("Life tab scraping error: %s", exc)

        return opinions

    # ------------------------------------------------------------------
    # Company posts
    # ------------------------------------------------------------------

    def _scrape_company_posts(self) -> List[Opinion]:
        opinions: List[Opinion] = []
        logger.info("LinkedIn: scraping company posts")
        collected = 0
        try:
            self.driver.get(COMPANY_POSTS_URL)
            random_delay(3, 5)

            for _ in range(SCRAPER["max_pages"]):
                posts = self.driver.find_elements(
                    By.CSS_SELECTOR, "div.feed-shared-update-v2"
                )
                for post in posts[collected:]:
                    opinion = self._extract_post_opinion(post, COMPANY_POSTS_URL)
                    if opinion:
                        opinions.append(opinion)
                collected = len(posts)
                if collected >= self.max_posts:
                    break
                self._scroll_page(scrolls=2)
                random_delay(2, 4)

        except Exception as exc:
            logger.warning("Company posts scraping error: %s", exc)

        return opinions

    # ------------------------------------------------------------------
    # Extraction helpers
    # ------------------------------------------------------------------

    def _extract_post_opinion(self, element, url: str) -> Optional[Opinion]:
        try:
            text = element.text.strip()
            if not text or len(text) < 20:
                return None

            # Try to get author name
            author = None
            try:
                author_el = element.find_element(
                    By.CSS_SELECTOR, "span.feed-shared-actor__name, span.org-life__name"
                )
                author = author_el.text.strip() or None
            except NoSuchElementException:
                pass

            # Try role
            role = None
            try:
                role_el = element.find_element(
                    By.CSS_SELECTOR, "span.feed-shared-actor__description, span.org-life__title"
                )
                role = role_el.text.strip() or None
            except NoSuchElementException:
                pass

            return Opinion(
                source="linkedin",
                company=COMPANY["name"],
                author=author,
                role=role,
                location=None,
                rating=None,
                title=None,
                text=text[:2000],
                pros=None,
                cons=None,
                date=None,
                url=url,
            )
        except Exception as exc:
            logger.debug("Could not extract LinkedIn post: %s", exc)
            return None

    def _scroll_page(self, scrolls: int = 3) -> None:
        for _ in range(scrolls):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            random_delay(1.5, 3)
