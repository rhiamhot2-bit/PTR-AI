"""Discord command for the stone-seat thickness correction validator."""

from pathlib import Path

from utils.seat_thickness_correction_validator_generator import (
    prepare_seat_thickness_correction_validator,
    save_seat_thickness_correction_validator,
)


async def cadseatthicknesscheck_command(ctx):
    """Create a report-only Rhino validator for the trial stone seat."""
    memory_root = Path(ctx.bot.ptr_config.memory_root)
    script_path, report_path, script = prepare_seat_thickness_correction_validator(memory_root)
    save_seat_thickness_correction_validator(script_path, script)
    await ctx.send(
        "🔎 สร้าง Seat Thickness Correction Validator แล้ว\n"
        "ตรวจ Closed Brep, Naked Edges และความหนาขั้นต่ำ โดยไม่แก้ ไม่ Union และไม่ Export\n"
        f"Report: {report_path}",
        file=__import__("discord").File(str(script_path)),
    )
