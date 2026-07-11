"""Handler for the !cadbrief command."""

from discord.ext import commands

from utils.cadbrief import format_cad_brief, parse_cad_brief
from utils.cadbrief_memory import save_cad_brief


async def cadbrief_command(
    ctx: commands.Context,
    *,
    request: str | None = None,
) -> None:
    """Build, save, and reply with a structured jewelry CAD brief."""
    prompt = (request or "").strip()
    if not prompt:
        await ctx.reply(
            "กรุณาใส่รายละเอียด เช่น "
            "!cadbrief แหวนไซซ์ 52 ทอง 18K มรกต Oval 8x6 มม. หนามเตย 4 เตย"
        )
        return

    brief = parse_cad_brief(prompt)
    config = ctx.bot.ptr_config  # type: ignore[attr-defined]
    saved_path = save_cad_brief(
        memory_root=config.memory_root,
        brief=brief,
        user_name=str(ctx.author),
    )
    response = f"{format_cad_brief(brief)}\nบันทึกแล้ว: {saved_path}"
    await ctx.reply(response[:2000])
