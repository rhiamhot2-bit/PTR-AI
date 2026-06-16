"""Client for sending Discord command payloads to n8n."""

from __future__ import annotations

from typing import Any

import requests


def send_to_n8n(webhook_url: str, payload: dict[str, Any], timeout: int = 30) -> dict[str, Any]:
    """POST a command payload to n8n and return a normalized response."""
    if not webhook_url:
        return {
            "ok": False,
            "message": "N8N_WEBHOOK_URL is not configured. Add it to your .env file.",
        }

    try:
        response = requests.post(webhook_url, json=payload, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        return {"ok": False, "message": f"n8n webhook request failed: {exc}"}

    if not response.content:
        return {"ok": True, "message": "Request sent to n8n successfully."}

    try:
        data = response.json()
    except ValueError:
        return {"ok": True, "message": response.text[:1900]}

    if isinstance(data, dict):
        return {"ok": True, **data}
    return {"ok": True, "message": str(data)}
