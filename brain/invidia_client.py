"""
AI NEWS FACTORY
CENTRAL NVIDIA AI CLIENT

Uses 4 NVIDIA API keys with automatic failover.

Key 1 → Key 2 → Key 3 → Key 4
"""

import os
import logging
import requests


logger = logging.getLogger("NewsFactory.NVIDIA")


class NVIDIAClient:

    def __init__(self):

        self.name = "NVIDIA Brain"

        self.base_url = (
            "https://integrate.api.nvidia.com/v1"
        )

        self.model = os.getenv(
            "NVIDIA_MODEL",
            "meta/llama-3.1-70b-instruct"
        )

        self.keys = []

        # Load the 4 NVIDIA keys
        for number in range(1, 5):

            key = os.getenv(
                f"NVIDIA_API_KEY_{number}"
            )

            if key:

                key = key.strip()

                if key:
                    self.keys.append(key)

        if not self.keys:

            raise RuntimeError(
                "No NVIDIA API keys found. "
                "Set NVIDIA_API_KEY_1 through "
                "NVIDIA_API_KEY_4."
            )

        self.current_key = 0

        self.timeout = 60

        logger.info(
            "NVIDIA Brain loaded with %s API keys.",
            len(self.keys)
        )

    # =====================================================
    # ASK NVIDIA
    # =====================================================

    def ask(
        self,
        prompt,
        system="You are an AI newsroom assistant.",
        temperature=0.2,
        max_tokens=2000
    ):

        messages = [

            {
                "role": "system",
                "content": system
            },

            {
                "role": "user",
                "content": prompt
            }

        ]

        return self.generate(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

    # =====================================================
    # GENERATE
    # =====================================================

    def generate(
        self,
        messages,
        temperature=0.2,
        max_tokens=2000
    ):

        total_keys = len(
            self.keys
        )

        last_error = None

        # Try every NVIDIA key
        for attempt in range(total_keys):

            key_index = (
                self.current_key + attempt
            ) % total_keys

            key = self.keys[
                key_index
            ]

            logger.info(
                "Trying NVIDIA key %s/%s",
                key_index + 1,
                total_keys
            )

            try:

                result = self._request(
                    key=key,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                # Remember successful key
                self.current_key = key_index

                return result

            except Exception as error:

                last_error = error

                logger.warning(
                    "NVIDIA key %s failed. "
                    "Trying next key.",
                    key_index + 1
                )

        raise RuntimeError(
            "All NVIDIA API keys failed. "
            f"Last error: {last_error}"
        )

    # =====================================================
    # API REQUEST
    # =====================================================

    def _request(
        self,
        key,
        messages,
        temperature,
        max_tokens
    ):

        url = (
            self.base_url
            + "/chat/completions"
        )

        headers = {

            "Authorization":
                f"Bearer {key}",

            "Content-Type":
                "application/json",

            "Accept":
                "application/json"
        }

        payload = {

            "model":
                self.model,

            "messages":
                messages,

            "temperature":
                temperature,

            "max_tokens":
                max_tokens
        }

        response = requests.post(

            url,

            headers=headers,

            json=payload,

            timeout=self.timeout
        )

        if not response.ok:

            raise RuntimeError(
                f"NVIDIA HTTP "
                f"{response.status_code}: "
                f"{response.text[:300]}"
            )

        data = response.json()

        choices = data.get(
            "choices",
            []
        )

        if not choices:

            raise RuntimeError(
                "NVIDIA returned no choices."
            )

        content = (
            choices[0]
            .get("message", {})
            .get("content", "")
        )

        if not content:

            raise RuntimeError(
                "NVIDIA returned empty content."
            )

        return content.strip()

    # =====================================================
    # STATUS
    # =====================================================

    def status(self):

        return {

            "provider":
                "NVIDIA",

            "model":
                self.model,

            "keys_configured":
                len(self.keys),

            "active_key":
                self.current_key + 1,

            "status":
                "READY"
        }
