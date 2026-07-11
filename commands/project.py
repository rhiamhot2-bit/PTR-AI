from discord.ext import commands

from utils.project_memory import create_project


async def project_command(
    ctx: commands.Context,
    *,
    project: str | None = None,
) -> None:
    if not project:
        await ctx.send("Usage:\n!project Ahmed Royal_Ring")
        return

    parts = project.split(maxsplit=1)
    if len(parts) < 2:
        await ctx.send("Example:\n!project Ahmed Royal_Ring")
        return

    customer, project_name = parts
    config = ctx.bot.ptr_config  # type: ignore[attr-defined]
    folder = create_project(config.memory_root, customer, project_name)

    await ctx.send(
        f"📁 Project Created\n\n"
        f"Customer : {customer}\n"
        f"Project : {project_name}\n\n"
        f"Saved : {folder}"
    )
