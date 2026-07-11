"""Configuration helpers for PTR AI."""

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Config:
    """Runtime configuration loaded from environment variables."""

    discord_token: str
    n8n_webhook_url: str
    memory_root: Path
    command_prefix: str = "!"
    request_timeout_seconds: int = 30


def load_dotenv(path: str = ".env") -> None:
    """Load KEY=VALUE pairs from a .env file without overwriting existing env vars."""
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _positive_int(value: str, name: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be a whole number.") from exc
    if parsed <= 0:
        raise RuntimeError(f"{name} must be greater than zero.")
    return parsed


def load_config() -> Config:
    """Load and validate bot configuration from .env and environment variables."""
    load_dotenv()
    return Config(
        discord_token=os.getenv("DISCORD_TOKEN", "").strip(),
        n8n_webhook_url=os.getenv("N8N_WEBHOOK_URL", "").strip(),
        memory_root=Path(os.getenv("MEMORY_ROOT", "./data/memory")).expanduser(),
        command_prefix=os.getenv("COMMAND_PREFIX", "!").strip() or "!",
        request_timeout_seconds=_positive_int(
            os.getenv("REQUEST_TIMEOUT_SECONDS", "30"),
            "REQUEST_TIMEOUT_SECONDS",
        ),
    )
