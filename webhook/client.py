"""Client for sending Discord command payloads to n8n."""

from __future__ import annotations

import json
from typing import Any

import aiohttp


async def send_to_n8n(
    webhook_url: str,
    payload: dict[str, Any],
    timeout: int = 30,
) -> dict[str, Any]:
    """POST a command payload to n8n and return a normalized response."""
    if not webhook_url:
        return {
            "ok": False,
            "message": "N8N_WEBHOOK_URL is not configured. Add it to your .env file.",
        }

    client_timeout = aiohttp.ClientTimeout(total=timeout)
    try:
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            async with session.post(webhook_url, json=payload) as response:
                response.raise_for_status()
                body = await response.text()
                content_type = response.headers.get("Content-Type", "")
    except (aiohttp.ClientError, TimeoutError) as exc:
        return {"ok": False, "message": f"n8n webhook request failed: {exc}"}

    if not body:
        return {"ok": True, "message": "Request sent to n8n successfully."}

    if "application/json" not in content_type.lower():
        return {"ok": True, "message": body[:1900]}

    try:
        data = json.loads(body)
    except ValueError:
        return {"ok": True, "message": body[:1900]}

    if isinstance(data, dict):
        return {"ok": True, **data}
    return {"ok": True, "message": str(data)}
