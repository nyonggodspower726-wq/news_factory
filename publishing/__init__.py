"""
AI NEWS FACTORY
PUBLISHING PACKAGE
"""

from .website_publisher import (
    WebsitePublisher,
    create_website_publisher,
)

from .social_publisher import (
    SocialPublisher,
    create_social_publisher,
)

from .reddit_publisher import (
    RedditPublisher,
    create_reddit_publisher,
)

from .wordpress_publisher import (
    WordPressPublisher,
    create_wordpress_publisher,
)

from .github_publisher import (
    GitHubPublisher,
    create_github_publisher,
)


__all__ = [

    "WebsitePublisher",
    "create_website_publisher",

    "SocialPublisher",
    "create_social_publisher",

    "RedditPublisher",
    "create_reddit_publisher",

    "WordPressPublisher",
    "create_wordpress_publisher",

    "GitHubPublisher",
    "create_github_publisher",
]
