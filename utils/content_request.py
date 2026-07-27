"""Build structured Content Agent requests aligned with PTR-CONTENT-STD v2.0."""

from __future__ import annotations

from dataclasses import asdict, dataclass

SUPPORTED_PLATFORMS = (
    "tiktok",
    "youtube_shorts",
    "facebook_reels",
)

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
    "youtube shorts": "youtube_shorts",
    "shorts": "youtube_shorts",
    "ยูทูปชอร์ต": "youtube_shorts",
    "facebook reels": "facebook_reels",
    "reels": "facebook_reels",
    "เฟซบุ๊กรีล": "facebook_reels",
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
    """Portable, review-first request sent from Discord to n8n."""

    topic: str
    platforms: tuple[str, ...]
    styles: tuple[str, ...]
    mode: str = "founder_presenter"
    language: str = "th"
    spoken_language: str = "thai"
    duration_seconds: int = 45
    business_domain: str = "jewelry"
    knowledge_mode: str = "jewelry_expert"
    presenter: str = "คุณเทียม"
    assistant_persona: str = "PTR AI"
    access_tier: str = "community"
    status: str = "needs_review"
    human_approval_required: bool = True
    auto_publish: bool = False
    output_format: str = "ptr_content_contract_v1"
    asset_ids: tuple[str, ...] = ()
    asset_search_query: str = ""
    founder_visible: str = "optional"
    audio_permission: str = "unknown"
    usage_rights: str = "unknown"

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["platforms"] = list(self.platforms)
        data["styles"] = list(self.styles)
        data["asset_ids"] = list(self.asset_ids)
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
        if (
            f"{seconds} วินาที" in lowered
            or f"{seconds}s" in lowered
            or f"{seconds} sec" in lowered
        ):
            return seconds
    return 45


def _detect_access_tier(text: str) -> str:
    lowered = text.lower()
    if any(term in lowered for term in ("ภายใน", "internal", "ทีมงาน")):
        return "internal"
    if any(term in lowered for term in ("ขาย", "ลูกค้า", "professional", "พรีเมียม")):
        return "professional"
    return "community"


def _detect_mode(text: str) -> str:
    lowered = text.lower()
    if any(term in lowered for term in ("คลิปเก่า", "วิดีโอเดิม", "asset", "ไฟล์เดิม")):
        return "asset_reuse"
    if any(term in lowered for term in ("ถามตอบ", "คุณเทียมถาม", "ptr ai ตอบ")):
        return "ai_partner"
    if any(term in lowered for term in ("cad", "rhino", "matrixgold", "เตย", "กะเปาะ")):
        return "jewelry_expert"
    return "founder_presenter"


def build_content_brief(request: str) -> ContentBrief:
    """Build a safe content brief from natural language without inventing facts."""
    topic = request.strip()
    if not topic:
        raise ValueError("Content topic is required")

    return ContentBrief(
        topic=topic,
        platforms=_detect_platforms(topic),
        styles=_detect_styles(topic),
        mode=_detect_mode(topic),
        duration_seconds=_detect_duration(topic),
        access_tier=_detect_access_tier(topic),
        asset_search_query=topic if _detect_mode(topic) == "asset_reuse" else "",
    )
