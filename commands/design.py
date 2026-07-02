
"""Handler for the !design command."""

from discord.ext import commands

from commands.common import dispatch_jewelry_command
from utils.memory import save_design_memory


async def design_command(ctx: commands.Context, *, request: str | None = None) -> None:
    """Forward !design requests to n8n and save memory."""
    
    prompt = request or ""

    save_design_memory(
        command="design",
        prompt=prompt,
        user_name=str(ctx.author)
    )

    await dispatch_jewelry_command(ctx, "design", request)