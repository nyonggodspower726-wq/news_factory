"""
AI NEWS FACTORY
Configuration

All global settings live here.
Sensitive API keys should be stored in environment variables.
"""

import os


# =========================================================
# FACTORY IDENTITY
# =========================================================

FACTORY_NAME = "AI NEWS FACTORY"
VERSION = "1.0.0"


# =========================================================
# ENVIRONMENT
# =========================================================

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

DEBUG = ENVIRONMENT != "production"


# =========================================================
# AI SETTINGS
# =========================================================

AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")

AI_API_KEY = os.getenv("AI_API_KEY", "")

AI_MODEL = os.getenv(
    "AI_MODEL",
    "gpt-5"
)


# =========================================================
# NEWS SETTINGS
# =========================================================

NEWS_LANGUAGE = "en"

DEFAULT_COUNTRY = "Nigeria"

MAX_STORIES_PER_SCAN = 50

MIN_STORY_SCORE = 70


# =========================================================
# NEWS COLLECTION
# =========================================================

RSS_SCAN_INTERVAL = 300  # 5 minutes

REQUEST_TIMEOUT = 20


# =========================================================
# ARTICLE SETTINGS
# =========================================================

MIN_ARTICLE_WORDS = 700

MAX_ARTICLE_WORDS = 1800

DEFAULT_AUTHOR = "News Factory"


# =========================================================
# PSYCHOLOGY / ENGAGEMENT
# =========================================================

ENABLE_READER_PSYCHOLOGY = True

TARGET_READING_TIME_MINUTES = 4

ENABLE_ENGAGEMENT_ANALYSIS = True


# =========================================================
# PUBLISHING
# =========================================================

AUTO_PUBLISH = False

# IMPORTANT:
# We keep this FALSE while developing.
# Once the factory is proven reliable, we can enable
# automatic publishing.

PUBLISH_DRAFTS = True


# =========================================================
# WEBSITE
# =========================================================

WEBSITE_ENABLED = False

WEBSITE_URL = os.getenv(
    "WEBSITE_URL",
    ""
)

WEBSITE_API_KEY = os.getenv(
    "WEBSITE_API_KEY",
    ""
)


# =========================================================
# SOCIAL MEDIA
# =========================================================

SOCIAL_PUBLISHING_ENABLED = False

FACEBOOK_ENABLED = False
INSTAGRAM_ENABLED = False
X_ENABLED = False
YOUTUBE_ENABLED = False
TIKTOK_ENABLED = False
TELEGRAM_ENABLED = False
REDDIT_ENABLED = False


# =========================================================
# DATABASE
# =========================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "news_factory.db"
)


# =========================================================
# LOGGING
# =========================================================

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO"
)


# =========================================================
# SAFETY
# =========================================================

ENABLE_FACT_CHECKING = True

ENABLE_SOURCE_VERIFICATION = True

ENABLE_DUPLICATE_DETECTION = True

ENABLE_CITATION_CHECKING = True

ENABLE_FINAL_EDITOR = True


# =========================================================
# DEVELOPMENT
# =========================================================

TEST_MODE = True

ALLOW_UNVERIFIED_PUBLISHING = False
