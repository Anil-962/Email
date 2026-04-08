#!/usr/bin/env python3
"""OpenEnv inference client for Gym-style backend endpoints.

Implements:
- reset()
- step(action)
- get_state()

Uses:
- requests
- configurable base URL (constructor arg or ENV_URL)
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import requests

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore[assignment]


DEFAULT_BASE_URL = os.environ.get("ENV_URL", "http://127.0.0.1:7860")
DEFAULT_TIMEOUT = float(os.environ.get("ENV_TIMEOUT", "10"))
DEFAULT_MODEL = os.environ.get("MODEL_NAME", "gpt-4o-mini")
_LOG = logging.getLogger("openenv.inference")
if not _LOG.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


class OpenEnvInferenceClient:
    """Tiny HTTP client for OpenEnv-compatible FastAPI backends."""

    def __init__(self, base_url: str = DEFAULT_BASE_URL, timeout: float = DEFAULT_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(self, method: str, endpoint: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(
                method=method,
                url=url,
                json=payload,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            return {
                "ok": False,
                "endpoint": endpoint,
                "status_code": None,
                "data": None,
                "error": f"Request failed: {exc}",
            }

        try:
            body = response.json()
        except ValueError:
            body = None

        if not response.ok:
            return {
                "ok": False,
                "endpoint": endpoint,
                "status_code": response.status_code,
                "data": body,
                "error": f"HTTP {response.status_code}",
            }

        return {
            "ok": True,
            "endpoint": endpoint,
            "status_code": response.status_code,
            "data": body,
            "error": None,
        }

    def reset(self) -> dict[str, Any]:
        """Reset environment state and return initial observation payload."""
        return self._request("POST", "/reset")

    def step(self, action: str | dict[str, Any]) -> dict[str, Any]:
        """Send one step action and return observation/reward/done payload."""
        payload = action if isinstance(action, dict) else {"message": action}
        return self._request("POST", "/step", payload=payload)

    def get_state(self) -> dict[str, Any]:
        """Return current environment state."""
        return self._request("GET", "/state")


_default_client = OpenEnvInferenceClient()


def suggest_action(context: str = "default rollout step") -> str:
    """
    Optional AI action generator with deterministic fallback.
    Falls back safely if model/client/key is unavailable.
    """
    fallback = "hello from inference.py"
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("HF_TOKEN")
    if OpenAI is None or not api_key:
        return fallback

    try:
        client = OpenAI(
            api_key=api_key,
            base_url=os.environ.get("API_BASE_URL", "https://router.huggingface.co/v1"),
        )
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "Generate one short safe action string."},
                {"role": "user", "content": f"Context: {context}"},
            ],
            temperature=0.2,
        )
        content = (response.choices[0].message.content or "").strip()
        return content or fallback
    except Exception as exc:
        _LOG.warning("AI action generation failed, using fallback action: %s", exc)
        return fallback


def reset() -> dict[str, Any]:
    """Module-level reset() helper."""
    return _default_client.reset()


def step(action: str | dict[str, Any]) -> dict[str, Any]:
    """Module-level step(action) helper."""
    return _default_client.step(action)


def get_state() -> dict[str, Any]:
    """Module-level get_state() helper."""
    return _default_client.get_state()


def main() -> None:
    """Quick smoke run against the configured backend."""
    client = OpenEnvInferenceClient()
    action = suggest_action("smoke test")
    result = {
        "reset": client.reset(),
        "step": client.step(action),
        "state": client.get_state(),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
