import logging
import os
from typing import Any, Dict, List
from urllib.parse import quote

import requests


logger = logging.getLogger("NewsFactory.SearchDiscovery")


class SearchDiscoveryEngine:
    """Notify participating search engines about newly published URLs."""

    def __init__(self) -> None:
        self.name = "Search Discovery Engine"
        self.version = "1.0.0"

        self.indexnow_endpoint = os.getenv(
            "INDEXNOW_ENDPOINT",
            "https://api.indexnow.org/indexnow",
        ).strip()

        self.indexnow_key = os.getenv(
            "INDEXNOW_KEY",
            "",
        ).strip()

        self.site_url = os.getenv(
            "GITHUB_SITE_URL",
            "",
        ).strip().rstrip("/")

        self.key_location = os.getenv(
            "INDEXNOW_KEY_LOCATION",
            "",
        ).strip()

        self.timeout = 30

    def status(self) -> Dict[str, Any]:
        configured = bool(
            self.indexnow_endpoint
            and self.indexnow_key
            and self.site_url
        )

        return {
            "engine": self.name,
            "version": self.version,
            "status": "READY" if configured else "NOT_CONFIGURED",
            "configured": configured,
            "indexnow_endpoint": self.indexnow_endpoint,
            "site_url": self.site_url,
            "key_configured": bool(self.indexnow_key),
            "key_location": self.key_location,
        }

    def submit(
        self,
        url: str,
    ) -> Dict[str, Any]:
        """Notify IndexNow about one added or updated URL."""

        url = str(url or "").strip()

        if not url:
            return self._fail("URL is missing.")

        if not self.indexnow_key:
            return self._fail("INDEXNOW_KEY is not configured.")

        if not self.site_url:
            return self._fail("GITHUB_SITE_URL is not configured.")

        if not url.startswith(self.site_url + "/"):
            return self._fail(
                "URL does not belong to the configured site."
            )

        params = {
            "url": url,
            "key": self.indexnow_key,
        }

        if self.key_location:
            params["keyLocation"] = self.key_location

        try:
            response = requests.get(
                self.indexnow_endpoint,
                params=params,
                timeout=self.timeout,
            )

            if response.status_code not in {200, 202}:
                return self._fail(
                    f"IndexNow returned HTTP {response.status_code}: "
                    f"{response.text[:300]}"
                )

            return {
                "status": "DISCOVERY_SUBMITTED",
                "submitted": True,
                "engine": self.name,
                "version": self.version,
                "url": url,
                "http_status": response.status_code,
            }

        except requests.RequestException as exc:
            logger.exception(
                "INDEXNOW_SUBMISSION_FAILED | url=%s",
                url,
            )

            return self._fail(
                f"IndexNow request failed: {exc}"
            )

    def submit_many(
        self,
        urls: List[str],
    ) -> Dict[str, Any]:
        """Notify IndexNow about multiple changed URLs."""

        unique = []
        seen = set()

        for url in urls or []:
            url = str(url or "").strip()

            if not url or url in seen:
                continue

            seen.add(url)
            unique.append(url)

        results = [
            self.submit(url)
            for url in unique
        ]

        successful = [
            item
            for item in results
            if item.get("submitted")
        ]

        return {
            "status": "DISCOVERY_BATCH_COMPLETE",
            "submitted": len(successful),
            "attempted": len(results),
            "results": results,
        }

    def _fail(self, error: str) -> Dict[str, Any]:
        return {
            "status": "DISCOVERY_FAILED",
            "submitted": False,
            "engine": self.name,
            "version": self.version,
            "error": error,
        }


search_discovery = SearchDiscoveryEngine()
