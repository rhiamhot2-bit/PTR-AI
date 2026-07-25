"""Utilities for turning a Discord !content request into a structured V2 brief."""

from __future__ import annotations

from dataclasses import asdict, dataclass

SUPPORTED_PLATFORMS = ("tiktok", "youtube_shorts", "facebook_reels")
SUPPORTED_STYLES = (
    "education",
    "tutorial",
    "news",
    "story",
    "motivation",
    "luxury",
    "jewelry",
    "ai",
    "marketing",
)
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
_STYLE_ALIASES = {
    "ความรู้": "education",
    "ให้ความรู้": "education",
    "สอน": "tutorial",
    "tutorial": "tutorial",
    "ข่าว": "news",
    "story": "story",
    "เรื่องเล่า": "story",
    "กำลังใจ": "motivation",
    "motivation": "motivation",
    "หรู": "luxury",
    "luxury": "luxury",
    "จิวเวลรี่": "jewelry",
    "jewelry": "jewelry",
    "ai": "ai",
    "เอไอ": "ai",
    "การตลาด": "marketing",
    "marketing": "marketing",
}


@dataclass(frozen=True)
class ContentBrief:
    """Portable Content Agent V2 request sent to n8n."""

    topic: str
    platforms: tuple[str, ...]
    styles: tuple[str, ...]
    language: str = "th"
    spoken_language: str = "thai"
    duration_seconds: int = 45
    business_domain: str = "jewelry"
    knowledge_mode: str = "jewelry_expert"
    presenter_mode: str = "thiam_plus_ptr_ai"
    approval_required: bool = True
    auto_publish: bool = False
    output_format: str = "content_pack_v2"

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["platforms"] = list(self.platforms)
        data["styles"] = list(self.styles)
        return data


def _detect_platforms(text: str) -> tuple[str, ...]:
    lowered = text.lower()
    detected: list[str] = []
    for alias, platform in _PLATFORM_ALIASES.items():
        if alias in lowered and platform not in detected:
            detected.append(platform)
    return tuple(detected) or SUPPORTED_PLATFORMS


def _detect_styles(text: str) -> tuple[str, ...]:
    lowered = text.lower()
    detected: list[str] = []
    for alias, style in _STYLE_ALIASES.items():
        if alias in lowered and style not in detected:
            detected.append(style)
    return tuple(detected) or ("education", "jewelry", "ai")


def _detect_duration(text: str) -> int:
    lowered = text.lower()
    for seconds in (8, 15, 30, 45, 60, 90):
        if f"{seconds} วินาที" in lowered or f"{seconds}s" in lowered or f"{seconds} sec" in lowered:
            return seconds
    return 45


def build_content_brief(request: str) -> ContentBrief:
    """Build a safe, review-first V2 brief from natural language."""
    topic = request.strip()
    if not topic:
        raise ValueError("Content topic is required")
    return ContentBrief(
        topic=topic,
        platforms=_detect_platforms(topic),
        styles=_detect_styles(topic),
        duration_seconds=_detect_duration(topic),
    )
