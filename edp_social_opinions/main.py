"""
EDP Social Opinions Collector
==============================
Collects employee opinions about EDP from Glassdoor, Indeed, LinkedIn,
and Twitter/X, then stores the results to CSV and JSON.

Usage
-----
    # Run once immediately
    python main.py

    # Run on a recurring schedule (every N hours, default 24)
    python main.py --schedule

    # Run only specific sources
    python main.py --sources glassdoor indeed

    # Override schedule interval
    python main.py --schedule --interval 12
"""

import argparse
import logging
import sys
from datetime import datetime
from typing import List

import schedule
import time

import config
from src.models.opinion import Opinion
from src.scrapers.glassdoor_scraper import GlassdoorScraper
from src.scrapers.indeed_scraper import IndeedScraper
from src.scrapers.linkedin_scraper import LinkedInScraper
from src.scrapers.social_media_scraper import SocialMediaScraper
from src.utils.data_handler import DataHandler

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("edp_opinions_collector.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Scraper registry
# ---------------------------------------------------------------------------

SCRAPERS = {
    "glassdoor": GlassdoorScraper,
    "indeed": IndeedScraper,
    "linkedin": LinkedInScraper,
    "twitter": SocialMediaScraper,
}

# ---------------------------------------------------------------------------
# Core collection routine
# ---------------------------------------------------------------------------


def collect(sources: List[str]) -> dict:
    """Run all requested scrapers and persist the results. Returns a summary dict."""
    logger.info("=" * 60)
    logger.info("EDP Social Opinions — collection started (%s)", datetime.utcnow().isoformat())
    logger.info("Sources: %s", ", ".join(sources))
    logger.info("=" * 60)

    all_opinions: List[Opinion] = []

    for source in sources:
        scraper_cls = SCRAPERS.get(source)
        if scraper_cls is None:
            logger.warning("Unknown source '%s', skipping.", source)
            continue
        try:
            logger.info("--- Running %s scraper ---", source.upper())
            opinions = scraper_cls().scrape()
            logger.info("%s: %d opinions collected.", source.upper(), len(opinions))
            all_opinions.extend(opinions)
        except Exception as exc:
            logger.error("%s scraper raised an exception: %s", source.upper(), exc, exc_info=True)

    handler = DataHandler(output_dir=config.OUTPUT_DIR)
    run_tag = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    summary = handler.save(all_opinions, run_tag=run_tag)

    logger.info("=" * 60)
    logger.info("Collection complete. Total opinions: %d", summary.get("total", 0))
    logger.info("By source: %s", summary.get("by_source", {}))
    logger.info("Avg ratings: %s", summary.get("avg_rating_by_source", {}))
    logger.info("=" * 60)

    return summary


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def parse_args():
    parser = argparse.ArgumentParser(
        description="Collect EDP employee opinions from social platforms."
    )
    parser.add_argument(
        "--sources",
        nargs="+",
        choices=list(SCRAPERS.keys()),
        default=config.SOURCES,
        help="Which sources to scrape (default: all)",
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Run on a recurring schedule instead of once.",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=config.SCHEDULE_INTERVAL_HOURS,
        help="Schedule interval in hours (default: %(default)s).",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.schedule:
        logger.info(
            "Scheduler mode: running every %d hour(s). First run starting now.",
            args.interval,
        )
        collect(args.sources)

        schedule.every(args.interval).hours.do(collect, sources=args.sources)

        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        collect(args.sources)


if __name__ == "__main__":
    main()
