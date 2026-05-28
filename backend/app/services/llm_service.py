"""
Thin LLM wrapper.

Uses Groq (free tier, OpenAI-compatible API) when GROQ_API_KEY is set,
otherwise OpenAI when OPENAI_API_KEY is set, otherwise returns None and the
caller falls back to the local question bank / templated feedback.

Designed so the rest of the codebase can stay LLM-agnostic.
"""
from __future__ import annotations

import json
from typing import Any

import httpx
from loguru import logger

from app.config import settings


GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"

OPENAI_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = "gpt-4o-mini"


def _provider() -> tuple[str, str, str, str] | None:
    """Returns (name, url, key, model) for the configured provider, or None."""
    if settings.groq_api_key:
        return "groq", GROQ_URL, settings.groq_api_key, GROQ_MODEL
    if settings.openai_api_key:
        return "openai", OPENAI_URL, settings.openai_api_key, OPENAI_MODEL
    return None


def is_available() -> bool:
    return _provider() is not None


def chat_json(
    system: str,
    user: str,
    *,
    temperature: float = 0.7,
    timeout_s: float = 25.0,
) -> dict | list | None:
    """
    Call the configured LLM and parse its response as JSON.
    Returns the parsed object, or None if no key is configured / request failed.
    """
    prov = _provider()
    if prov is None:
        logger.debug("No LLM key configured; chat_json() returning None.")
        return None

    name, url, key, model = prov
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    body: dict[str, Any] = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "response_format": {"type": "json_object"},
    }

    try:
        with httpx.Client(timeout=timeout_s) as client:
            r = client.post(url, headers=headers, json=body)
            r.raise_for_status()
            data = r.json()
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"LLM call ({name}) failed: {exc}")
        return None


def chat_text(
    system: str,
    user: str,
    *,
    temperature: float = 0.6,
    timeout_s: float = 25.0,
) -> str | None:
    """Like chat_json but returns plain text."""
    prov = _provider()
    if prov is None:
        return None

    name, url, key, model = prov
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    body: dict[str, Any] = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }

    try:
        with httpx.Client(timeout=timeout_s) as client:
            r = client.post(url, headers=headers, json=body)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"LLM call ({name}) failed: {exc}")
        return None
