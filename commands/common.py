"""Shared command helpers."""

from __future__ import annotations

from typing import Any

from discord.ext import commands

from webhook.client import send_to_n8n


async def dispatch_jewelry_command(
    ctx: commands.Context,
    command_name: str,
    request: str | None,
) -> None:
    """Send a Discord command request to the configured n8n webhook."""
    prompt = (request or "").strip()
    if not prompt:
        await ctx.reply(
            f"Please include a request. Example: "
            f"`!{command_name} Create a luxury gold necklace concept.`"
        )
        return

    config = ctx.bot.ptr_config  # type: ignore[attr-defined]
    payload: dict[str, Any] = {
        "command": command_name,
        "prompt": prompt,
        "business": "jewelry",
        "discord": {
            "user_id": str(ctx.author.id),
            "user_name": str(ctx.author),
            "channel_id": str(ctx.channel.id),
            "guild_id": str(ctx.guild.id) if ctx.guild else None,
            "message_id": str(ctx.message.id),
        },
    }

    async with ctx.typing():
        result = await send_to_n8n(
            config.n8n_webhook_url,
            payload,
            config.request_timeout_seconds,
        )

    status = "✅" if result.get("ok") else "⚠️"
    message = result.get("reply") or result.get("message") or "The request was processed by n8n."
    await ctx.reply(f"{status} **{command_name.title()}**\n{message}"[:2000])
