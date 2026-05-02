"""
Indeed employee review scraper for EDP.

Fetches company reviews using requests + BeautifulSoup.
Indeed renders reviews server-side, making them accessible without JavaScript.
"""

import logging
import re
import time
from typing import List, Optional

from bs4 import BeautifulSoup

from config import COMPANY, SCRAPER
from src.models.opinion import Opinion
from src.utils.browser_utils import build_session, random_delay

logger = logging.getLogger(__name__)

BASE_URL = "https://www.indeed.com"
# Indeed review pagination uses &start=0, 20, 40 …
REVIEWS_URL = f"{BASE_URL}/cmp/{COMPANY['indeed_slug']}/reviews?start={{start}}"
PAGE_SIZE = 20


class IndeedScraper:
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
        logger.info("Starting Indeed scrape for %s", COMPANY["name"])

        for page in range(self.max_pages):
            start = page * PAGE_SIZE
            url = REVIEWS_URL.format(start=start)
            logger.info("Indeed page %d/%d — %s", page + 1, self.max_pages, url)

            html = self._fetch_page(url)
            if not html:
                logger.warning("Empty response at start=%d, stopping.", start)
                break

            page_opinions = self._parse_page(html, url)
            if not page_opinions:
                logger.info("No reviews on page %d, stopping.", page + 1)
                break

            opinions.extend(page_opinions)
            logger.info("Collected %d reviews so far.", len(opinions))
            random_delay(self.delay_min, self.delay_max)

        logger.info("Indeed: %d total opinions collected.", len(opinions))
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
                logger.warning("Indeed fetch attempt %d failed: %s", attempt, exc)
                time.sleep(2 ** attempt)
        return None

    def _parse_page(self, html: str, page_url: str) -> List[Opinion]:
        soup = BeautifulSoup(html, "lxml")
        opinions: List[Opinion] = []

        # Indeed wraps each review in a <div data-tn-component="review">
        review_blocks = soup.find_all("div", attrs={"data-tn-component": "review"})
        if not review_blocks:
            # Fallback: look for review cards by class
            review_blocks = soup.find_all("div", class_=re.compile(r"cmp-Review", re.I))

        for block in review_blocks:
            opinion = self._parse_review_block(block, page_url)
            if opinion:
                opinions.append(opinion)

        return opinions

    def _parse_review_block(self, block, page_url: str) -> Optional[Opinion]:
        try:
            title = self._text(block.find("h2", class_=re.compile(r"title", re.I)))
            rating = self._parse_rating(block)
            date = self._text(block.find("time"))
            role = self._text(
                block.find("span", class_=re.compile(r"JobTitle|authorJobTitle", re.I))
            )
            location = self._text(
                block.find("span", class_=re.compile(r"location|authorLocation", re.I))
            )
            pros = self._text(
                block.find("span", class_=re.compile(r"pros", re.I))
            )
            cons = self._text(
                block.find("span", class_=re.compile(r"cons", re.I))
            )
            body = self._text(block.find("span", class_=re.compile(r"reviewText|description", re.I)))
            text = body or " | ".join(filter(None, [pros, cons]))

            employment_status = self._parse_employment_status(block)

            if not text and not title:
                return None

            return Opinion(
                source="indeed",
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
            logger.debug("Could not parse Indeed review block: %s", exc)
            return None

    @staticmethod
    def _text(tag) -> Optional[str]:
        if tag is None:
            return None
        txt = tag.get_text(separator=" ", strip=True)
        return txt if txt else None

    @staticmethod
    def _parse_rating(block) -> Optional[float]:
        # <meta itemprop="ratingValue" content="4"> or star svg aria-label="4 out of 5 stars"
        meta = block.find("meta", {"itemprop": "ratingValue"})
        if meta:
            try:
                return float(meta["content"])
            except (KeyError, ValueError):
                pass
        star = block.find(attrs={"aria-label": re.compile(r"star", re.I)})
        if star:
            match = re.search(r"([\d.]+)", star.get("aria-label", ""))
            if match:
                return float(match.group(1))
        return None

    @staticmethod
    def _parse_employment_status(block) -> Optional[str]:
        text = block.get_text(" ", strip=True).lower()
        if "former" in text or "ex-" in text:
            return "former"
        if "current" in text:
            return "current"
        return None
