"""
Glassdoor employee review scraper for EDP.

Fetches reviews from Glassdoor using requests + BeautifulSoup.
Glassdoor serves server-rendered HTML for the first page and requires
JavaScript for pagination; this scraper handles both paths.
"""

import logging
import re
import time
from typing import List, Optional

from bs4 import BeautifulSoup

from config import COMPANY, SCRAPER
from src.models.opinion import Opinion
from src.utils.browser_utils import build_session, build_selenium_driver, random_delay

logger = logging.getLogger(__name__)

BASE_URL = "https://www.glassdoor.com"
REVIEWS_URL = (
    f"{BASE_URL}/Reviews/{COMPANY['glassdoor_slug']}"
    f"-E{COMPANY['glassdoor_id']}_P{{page}}.htm"
)


class GlassdoorScraper:
    def __init__(self):
        self.session = build_session(SCRAPER.get("proxy_url"))
        self.max_pages = SCRAPER["max_pages"]
        self.delay_min = SCRAPER["request_delay_min"]
        self.delay_max = SCRAPER["request_delay_max"]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scrape(self) -> List[Opinion]:
        opinions: List[Opinion] = []
        logger.info("Starting Glassdoor scrape for %s", COMPANY["name"])

        for page in range(1, self.max_pages + 1):
            url = REVIEWS_URL.format(page=page)
            logger.info("Glassdoor page %d/%d — %s", page, self.max_pages, url)

            html = self._fetch_page(url)
            if not html:
                logger.warning("Empty response on page %d, stopping.", page)
                break

            page_opinions = self._parse_page(html, url)
            if not page_opinions:
                logger.info("No reviews found on page %d, stopping.", page)
                break

            opinions.extend(page_opinions)
            logger.info("Collected %d reviews so far.", len(opinions))
            random_delay(self.delay_min, self.delay_max)

        logger.info("Glassdoor: %d total opinions collected.", len(opinions))
        return opinions

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fetch_page(self, url: str) -> Optional[str]:
        for attempt in range(1, SCRAPER["max_retries"] + 1):
            try:
                resp = self.session.get(url, timeout=SCRAPER["timeout"])
                resp.raise_for_status()
                return resp.text
            except Exception as exc:
                logger.warning("Glassdoor fetch attempt %d failed: %s", attempt, exc)
                time.sleep(2 ** attempt)
        return None

    def _parse_page(self, html: str, page_url: str) -> List[Opinion]:
        soup = BeautifulSoup(html, "lxml")
        opinions: List[Opinion] = []

        # Glassdoor review containers use data-test="review"
        review_blocks = soup.find_all("li", {"data-test": re.compile(r"review", re.I)})
        if not review_blocks:
            # Fallback selector for layout variations
            review_blocks = soup.find_all("div", class_=re.compile(r"review", re.I))

        for block in review_blocks:
            opinion = self._parse_review_block(block, page_url)
            if opinion:
                opinions.append(opinion)

        return opinions

    def _parse_review_block(self, block, page_url: str) -> Optional[Opinion]:
        try:
            title = self._text(block.find(attrs={"data-test": "review-title"}))
            rating_tag = block.find("span", {"data-test": "starRating"})
            rating = self._parse_rating(rating_tag)
            pros = self._text(block.find(attrs={"data-test": "pros"}))
            cons = self._text(block.find(attrs={"data-test": "cons"}))
            date = self._text(block.find("time"))
            role = self._text(block.find(attrs={"data-test": "author-jobTitle"}))
            location = self._text(block.find(attrs={"data-test": "author-location"}))
            status_tag = block.find(attrs={"data-test": "author-employeeStatus"})
            status = self._text(status_tag)
            employment_status = _map_employment_status(status)
            text = " | ".join(filter(None, [pros, cons]))

            if not text and not title:
                return None

            return Opinion(
                source="glassdoor",
                company=COMPANY["name"],
                author=None,
                role=role,
                location=location,
                rating=rating,
                title=title,
                text=text,
                pros=pros,
                cons=cons,
                date=date,
                url=page_url,
                employment_status=employment_status,
            )
        except Exception as exc:
            logger.debug("Could not parse Glassdoor review block: %s", exc)
            return None

    @staticmethod
    def _text(tag) -> Optional[str]:
        if tag is None:
            return None
        txt = tag.get_text(separator=" ", strip=True)
        return txt if txt else None

    @staticmethod
    def _parse_rating(tag) -> Optional[float]:
        if tag is None:
            return None
        # Try aria-label="X.X" first
        label = tag.get("aria-label", "")
        match = re.search(r"([\d.]+)", label)
        if match:
            return float(match.group(1))
        text = tag.get_text(strip=True)
        match = re.search(r"([\d.]+)", text)
        return float(match.group(1)) if match else None


def _map_employment_status(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    raw_lower = raw.lower()
    if "former" in raw_lower or "ex-" in raw_lower or "antigo" in raw_lower:
        return "former"
    if "current" in raw_lower or "atual" in raw_lower:
        return "current"
    return None
