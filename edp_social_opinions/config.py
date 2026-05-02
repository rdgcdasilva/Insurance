import os
from dotenv import load_dotenv

load_dotenv()

COMPANY = {
    "name": "EDP",
    "aliases": ["EDP", "Energias de Portugal", "EDP Renewables", "EDPR", "EDP Brasil"],
    "glassdoor_id": "40415",
    "glassdoor_slug": "EDP-Reviews",
    "indeed_slug": "edp",
    "linkedin_company_id": "edp",
    "twitter_hashtags": ["#EDP", "#EDPRenewables", "#EnergiaEDP"],
    "twitter_keywords": ["EDP funcionários", "EDP empresa", "trabalhar na EDP", "EDP colaboradores"],
}

CREDENTIALS = {
    "linkedin_email": os.getenv("LINKEDIN_EMAIL", ""),
    "linkedin_password": os.getenv("LINKEDIN_PASSWORD", ""),
    "twitter_bearer_token": os.getenv("TWITTER_BEARER_TOKEN", ""),
    "twitter_api_key": os.getenv("TWITTER_API_KEY", ""),
    "twitter_api_secret": os.getenv("TWITTER_API_SECRET", ""),
    "twitter_access_token": os.getenv("TWITTER_ACCESS_TOKEN", ""),
    "twitter_access_secret": os.getenv("TWITTER_ACCESS_SECRET", ""),
}

SCRAPER = {
    "request_delay_min": 2.0,
    "request_delay_max": 5.0,
    "max_retries": 3,
    "timeout": 30,
    "max_pages": 10,
    "proxy_url": os.getenv("PROXY_URL", ""),
    "headless_browser": True,
}

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "data")
SCHEDULE_INTERVAL_HOURS = int(os.getenv("SCHEDULE_INTERVAL_HOURS", "24"))

SOURCES = ["glassdoor", "indeed", "linkedin", "twitter"]
