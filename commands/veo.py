"""Handler for the !veo command."""

from discord.ext import commands

from commands.common import dispatch_jewelry_command


async def veo_command(ctx: commands.Context, *, request: str | None = None) -> None:
    """Forward !veo requests to n8n."""
    await dispatch_jewelry_command(ctx, "veo", request)
