"""
AI NEWS FACTORY
CENTRAL SETTINGS

All environment-based configuration lives here.

Never hard-code API keys, passwords, or access tokens
inside the source code.
"""

import os
from dataclasses import dataclass


def _env(
    name: str,
    default: str = ""
) -> str:

    return os.getenv(
        name,
        default
    ).strip()


def _env_int(
    name: str,
    default: int
) -> int:

    try:

        return int(
            os.getenv(
                name,
                str(default)
            )
        )

    except (
        TypeError,
        ValueError
    ):

        return default


@dataclass
class Settings:

    # =====================================================
    # FACTORY
    # =====================================================

    app_name: str = _env(
        "NEWS_FACTORY_NAME",
        "AI News Factory"
    )

    environment: str = _env(
        "ENVIRONMENT",
        "production"
    )

    log_level: str = _env(
        "LOG_LEVEL",
        "INFO"
    )

    runtime_interval: int = _env_int(
        "NEWS_FACTORY_INTERVAL",
        900
    )

    # =====================================================
    # AI
    # =====================================================

    ai_api_key: str = _env(
        "AI_API_KEY"
    )

    ai_model: str = _env(
        "AI_MODEL",
        "gpt-5.6"
    )

    # =====================================================
    # WEBSITE
    # =====================================================

    news_site_url: str = _env(
        "NEWS_SITE_URL"
    )

    news_site_api_url: str = _env(
        "NEWS_SITE_API_URL"
    )

    news_site_api_key: str = _env(
        "NEWS_SITE_API_KEY"
    )

    # =====================================================
    # WORDPRESS
    # =====================================================

    wordpress_url: str = _env(
        "WORDPRESS_URL"
    )

    wordpress_username: str = _env(
        "WORDPRESS_USERNAME"
    )

    wordpress_app_password: str = _env(
        "WORDPRESS_APP_PASSWORD"
    )

    # =====================================================
    # GITHUB
    # =====================================================

    github_token: str = _env(
        "GITHUB_TOKEN"
    )

    github_repository: str = _env(
        "GITHUB_REPOSITORY"
    )

    github_branch: str = _env(
        "GITHUB_BRANCH",
        "main"
    )

    # =====================================================
    # REDDIT
    # =====================================================

    reddit_client_id: str = _env(
        "REDDIT_CLIENT_ID"
    )

    reddit_client_secret: str = _env(
        "REDDIT_CLIENT_SECRET"
    )

    reddit_username: str = _env(
        "REDDIT_USERNAME"
    )

    reddit_password: str = _env(
        "REDDIT_PASSWORD"
    )

    reddit_user_agent: str = _env(
        "REDDIT_USER_AGENT",
        "AI-News-Factory/1.0"
    )

    reddit_subreddit: str = _env(
        "REDDIT_SUBREDDIT"
    )

    # =====================================================
    # SOCIAL
    # =====================================================

    facebook_access_token: str = _env(
        "FACEBOOK_ACCESS_TOKEN"
    )

    facebook_page_id: str = _env(
        "FACEBOOK_PAGE_ID"
    )

    x_api_key: str = _env(
        "X_API_KEY"
    )

    x_api_secret: str = _env(
        "X_API_SECRET"
    )

    x_access_token: str = _env(
        "X_ACCESS_TOKEN"
    )

    x_access_secret: str = _env(
        "X_ACCESS_SECRET"
    )

    # =====================================================
    # MEDIA
    # =====================================================

    pexels_api_key: str = _env(
        "PEXELS_API_KEY"
    )

    unsplash_access_key: str = _env(
        "UNSPLASH_ACCESS_KEY"
    )

    # =====================================================
    # DATABASE
    # =====================================================

    database_url: str = _env(
        "DATABASE_URL",
        "news_factory.db"
    )

    # =====================================================
    # SECURITY
    # =====================================================

    secret_key: str = _env(
        "NEWS_FACTORY_SECRET"
    )

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(
        self
    ) -> dict:

        warnings = []

        if not self.ai_api_key:

            warnings.append(
                "AI_API_KEY is not configured."
            )

        if not (
            self.news_site_api_url
            or self.wordpress_url
            or self.github_repository
        ):

            warnings.append(
                "No website publishing destination is configured."
            )

        return {

            "valid":
                True,

            "warnings":
                warnings
        }


# =========================================================
# GLOBAL SETTINGS
# =========================================================

settings = Settings()


def get_settings() -> Settings:

    return settings
