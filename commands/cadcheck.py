"""Handler for the !cadcheck command."""

from discord.ext import commands

from utils.cad_rules import format_validation_report, validate_cad_request
from utils.cadcheck_memory import save_cad_check


async def cadcheck_command(ctx: commands.Context, *, request: str | None = None) -> None:
    prompt = (request or "").strip()
    if not prompt:
        await ctx.reply(
            "กรุณาใส่รายละเอียด เช่น !cadcheck แหวนไซซ์ 52 ทอง 18K มรกต "
            "Oval 8x6 มม. หนามเตย 4 เตย ก้านกว้าง 2.5 มม. "
            "ก้านหนา 1.8 มม. หนามเตยหนา 0.7 มม. ระยะเผื่อฝัง 0.1 มม."
        )
        return

    report = validate_cad_request(prompt)
    config = ctx.bot.ptr_config  # type: ignore[attr-defined]
    path = save_cad_check(config.memory_root, report, str(ctx.author))
    response = f"{format_validation_report(report)}\nบันทึกแล้ว: {path}"
    await ctx.reply(response[:2000])
