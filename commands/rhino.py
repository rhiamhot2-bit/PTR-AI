"""Handler for the !rhino command."""

from discord.ext import commands

from commands.common import dispatch_jewelry_command


async def rhino_command(ctx: commands.Context, *, request: str | None = None) -> None:
    """Forward !rhino requests to n8n."""
    await dispatch_jewelry_command(ctx, "rhino", request)
