"""Utilities for turning a Discord !content request into a structured brief."""

from __future__ import annotations

from dataclasses import asdict, dataclass

SUPPORTED_PLATFORMS = ("tiktok", "youtube_shorts", "facebook_reels")
_PLATFORM_ALIASES = {
    "tiktok": "tiktok",
    "ติ๊กต็อก": "tiktok",
    "youtube": "youtube_shorts",
    "youtube shorts": "youtube_shorts",
    "shorts": "youtube_shorts",
    "ยูทูป": "youtube_shorts",
    "facebook": "facebook_reels",
    "facebook reels": "facebook_reels",
    "reels": "facebook_reels",
    "เฟซบุ๊ก": "facebook_reels",
}


@dataclass(frozen=True)
class ContentBrief:
    """Portable content-generation request sent to n8n."""

    topic: str
    platforms: tuple[str, ...]
    language: str = "th"
    duration_seconds: int = 45
    approval_required: bool = True
    output_format: str = "content_pack_v1"

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["platforms"] = list(self.platforms)
        return data


def _detect_platforms(text: str) -> tuple[str, ...]:
    lowered = text.lower()
    detected: list[str] = []
    for alias, platform in _PLATFORM_ALIASES.items():
        if alias in lowered and platform not in detected:
            detected.append(platform)
    return tuple(detected) or SUPPORTED_PLATFORMS


def _detect_duration(text: str) -> int:
    lowered = text.lower()
    for seconds in (15, 30, 45, 60, 90):
        if f"{seconds} วินาที" in lowered or f"{seconds}s" in lowered or f"{seconds} sec" in lowered:
            return seconds
    return 45


def build_content_brief(request: str) -> ContentBrief:
    """Build a safe, review-first brief from the user's natural-language request."""
    topic = request.strip()
    if not topic:
        raise ValueError("Content topic is required")
    return ContentBrief(
        topic=topic,
        platforms=_detect_platforms(topic),
        duration_seconds=_detect_duration(topic),
    )
