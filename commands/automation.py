"""Handler for the !automation command."""

from discord.ext import commands

from commands.common import dispatch_jewelry_command


async def automation_command(ctx: commands.Context, *, request: str | None = None) -> None:
    """Forward !automation requests to n8n."""
    await dispatch_jewelry_command(ctx, "automation", request)
