"""Handler for the !content command."""

from discord.ext import commands

from commands.common import dispatch_jewelry_command


async def content_command(ctx: commands.Context, *, request: str | None = None) -> None:
    """Forward !content requests to n8n."""
    await dispatch_jewelry_command(ctx, "content", request)
