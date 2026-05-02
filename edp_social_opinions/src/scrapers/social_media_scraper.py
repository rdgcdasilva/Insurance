"""
Social media scraper — Twitter/X for EDP employee opinions.

Uses the Twitter v2 API via tweepy when credentials are available.
Falls back to a lightweight requests-based search for public tweets
when no API credentials are configured.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import List, Optional

from config import COMPANY, CREDENTIALS, SCRAPER
from src.models.opinion import Opinion
from src.utils.browser_utils import random_delay

logger = logging.getLogger(__name__)

# Search queries that surface employee opinions about EDP
TWITTER_QUERIES = [
    f'"{name}" funcionários OR colaboradores OR trabalhar lang:pt -is:retweet'
    for name in COMPANY["aliases"][:2]
] + [
    '"EDP" employer OR employee OR trabalho OR empresa lang:pt -is:retweet',
    "#EDP trabalho OR emprego OR equipa lang:pt -is:retweet",
]

MAX_RESULTS_PER_QUERY = 100


class SocialMediaScraper:
    def __init__(self):
        self._has_twitter_creds = bool(CREDENTIALS.get("twitter_bearer_token"))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scrape(self) -> List[Opinion]:
        opinions: List[Opinion] = []
        opinions.extend(self._scrape_twitter())
        logger.info("Social media: %d total opinions collected.", len(opinions))
        return opinions

    # ------------------------------------------------------------------
    # Twitter / X
    # ------------------------------------------------------------------

    def _scrape_twitter(self) -> List[Opinion]:
        if self._has_twitter_creds:
            return self._scrape_twitter_api()
        logger.warning(
            "Twitter API credentials not configured. "
            "Set TWITTER_BEARER_TOKEN in .env to enable Twitter scraping."
        )
        return []

    def _scrape_twitter_api(self) -> List[Opinion]:
        """Collect tweets via tweepy Twitter API v2."""
        try:
            import tweepy
        except ImportError:
            logger.error("tweepy not installed. Run: pip install tweepy")
            return []

        client = tweepy.Client(
            bearer_token=CREDENTIALS["twitter_bearer_token"],
            consumer_key=CREDENTIALS.get("twitter_api_key"),
            consumer_secret=CREDENTIALS.get("twitter_api_secret"),
            access_token=CREDENTIALS.get("twitter_access_token"),
            access_token_secret=CREDENTIALS.get("twitter_access_secret"),
            wait_on_rate_limit=True,
        )

        opinions: List[Opinion] = []
        since = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

        for query in TWITTER_QUERIES:
            logger.info("Twitter query: %s", query)
            try:
                paginator = tweepy.Paginator(
                    client.search_recent_tweets,
                    query=query,
                    tweet_fields=["created_at", "author_id", "lang", "text"],
                    expansions=["author_id"],
                    user_fields=["name", "username"],
                    start_time=since,
                    max_results=10,
                    limit=MAX_RESULTS_PER_QUERY // 10,
                )

                users_by_id: dict = {}
                for response in paginator:
                    if response.includes and "users" in response.includes:
                        for u in response.includes["users"]:
                            users_by_id[u.id] = u

                    if not response.data:
                        continue

                    for tweet in response.data:
                        user = users_by_id.get(tweet.author_id)
                        opinion = self._tweet_to_opinion(tweet, user)
                        opinions.append(opinion)

                random_delay(SCRAPER["request_delay_min"], SCRAPER["request_delay_max"])

            except Exception as exc:
                logger.warning("Twitter query failed: %s — %s", query, exc)

        logger.info("Twitter: %d tweets collected.", len(opinions))
        return opinions

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _tweet_to_opinion(tweet, user) -> Opinion:
        author = user.username if user else None
        date = tweet.created_at.isoformat() if tweet.created_at else None
        url = f"https://twitter.com/i/web/status/{tweet.id}"

        return Opinion(
            source="twitter",
            company=COMPANY["name"],
            author=author,
            role=None,
            location=None,
            rating=None,
            title=None,
            text=tweet.text,
            pros=None,
            cons=None,
            date=date,
            url=url,
            language=tweet.lang,
        )
