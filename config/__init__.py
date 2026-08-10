"""
AI NEWS FACTORY
CONFIG PACKAGE
"""

from .settings import (
    Settings,
    settings,
    get_settings,
)


# =========================================================
# FACTORY INFORMATION
# =========================================================

FACTORY_NAME = "AI NEWS FACTORY"
VERSION = "1.0.0"


__all__ = [
    "Settings",
    "settings",
    "get_settings",
    "FACTORY_NAME",
    "VERSION",
]
