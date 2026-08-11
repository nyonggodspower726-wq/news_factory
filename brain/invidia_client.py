"""
AI NEWS FACTORY
CENTRAL NVIDIA AI CLIENT

4 NVIDIA API keys with:

1. Round-robin rotation
2. Automatic failover
3. Rate-limit/error failover
4. Thread-safe key selection
5. Automatic return to Key 1 after Key 4
6. No API keys exposed in logs

Rotation:

Key 1 → Key 2 → Key 3 → Key 4 → Key 1...

If the selected key fails:

Key 1 → Key 2 → Key 3 → Key 4
"""

import os
import logging
import threading
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

        # =================================================
        # LOAD NVIDIA KEYS
        # =================================================

        self.keys = []

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
                "NVIDIA_API_KEY_4 in Railway Variables."
            )

        # =================================================
        # ROTATION STATE
        # =================================================

        self.current_key = 0

        self.timeout = 60

        self.lock = threading.Lock()

        # Statistics
        self.total_requests = 0
        self.total_failovers = 0

        self.key_successes = {
            index + 1: 0
            for index in range(
                len(self.keys)
            )
        }

        self.key_failures = {
            index + 1: 0
            for index in range(
                len(self.keys)
            )
        }

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

        if total_keys == 0:

            raise RuntimeError(
                "No NVIDIA API keys available."
            )

        # =================================================
        # SELECT NEXT KEY
        # =================================================

        with self.lock:

            start_index = (
                self.current_key
            )

            self.current_key = (
                self.current_key + 1
            ) % total_keys

            self.total_requests += 1

        logger.info(
            "NVIDIA request starting with "
            "key %s/%s.",
            start_index + 1,
            total_keys
        )

        last_error = None

        # =================================================
        # TRY KEYS
        # =================================================

        for attempt in range(
            total_keys
        ):

            key_index = (
                start_index + attempt
            ) % total_keys

            key = self.keys[
                key_index
            ]

            logger.info(
                "NVIDIA attempting key %s/%s.",
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

                # =========================================
                # SUCCESS
                # =========================================

                self.key_successes[
                    key_index + 1
                ] += 1

                logger.info(
                    "NVIDIA key %s succeeded.",
                    key_index + 1
                )

                return result

            except Exception as error:

                last_error = error

                self.key_failures[
                    key_index + 1
                ] += 1

                logger.warning(
                    "NVIDIA key %s failed. "
                    "Trying next key.",
                    key_index + 1
                )

                if attempt < (
                    total_keys - 1
                ):

                    self.total_failovers += 1

        # =================================================
        # ALL KEYS FAILED
        # =================================================

        logger.error(
            "All NVIDIA API keys failed."
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

        # =================================================
        # HTTP FAILURE
        # =================================================

        if not response.ok:

            raise RuntimeError(
                f"NVIDIA HTTP "
                f"{response.status_code}: "
                f"{response.text[:300]}"
            )

        # =================================================
        # JSON
        # =================================================

        data = response.json()

        choices = data.get(
            "choices",
            []
        )

        if not choices:

            raise RuntimeError(
                "NVIDIA returned no choices."
            )

        message = choices[0].get(
            "message",
            {}
        )

        content = message.get(
            "content",
            ""
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

            "rotation":
                "ROUND_ROBIN",

            "failover":
                True,

            "total_requests":
                self.total_requests,

            "total_failovers":
                self.total_failovers,

            "key_successes":
                dict(
                    self.key_successes
                ),

            "key_failures":
                dict(
                    self.key_failures
                ),

            "status":
                "READY"
        }
