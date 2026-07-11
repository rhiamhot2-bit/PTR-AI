"""Handler for the !design command."""

from discord.ext import commands

from commands.common import dispatch_jewelry_command
from utils.memory import save_design_memory


async def design_command(ctx: commands.Context, *, request: str | None = None) -> None:
    """Validate, save, and forward !design requests to n8n."""
    prompt = (request or "").strip()
    if not prompt:
        await ctx.reply(
            "Please include a request. Example: "
            "`!design Create a bridal ring with an emerald center stone.`"
        )
        return

    config = ctx.bot.ptr_config  # type: ignore[attr-defined]
    save_design_memory(
        memory_root=config.memory_root,
        command="design",
        prompt=prompt,
        user_name=str(ctx.author),
    )

    await dispatch_jewelry_command(ctx, "design", prompt)
