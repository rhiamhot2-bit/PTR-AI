"""Handler for the !business command."""

from discord.ext import commands

from commands.common import dispatch_jewelry_command


async def business_command(ctx: commands.Context, *, request: str | None = None) -> None:
    """Forward !business requests to n8n."""
    await dispatch_jewelry_command(ctx, "business", request)
