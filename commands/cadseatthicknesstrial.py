"""Discord command for a copy-only stone-seat thickness correction trial."""

from pathlib import Path

from utils.seat_thickness_correction_trial_generator import (
    prepare_seat_thickness_correction_trial,
    save_seat_thickness_correction_trial,
)


async def cadseatthicknesstrial_command(ctx):
    """Create a Rhino script that thickens a duplicate seat only."""
    memory_root = Path(ctx.bot.ptr_config.memory_root)
    script_path, report_path, script = prepare_seat_thickness_correction_trial(memory_root)
    save_seat_thickness_correction_trial(script_path, script)
    await ctx.send(
        "✅ สร้าง Seat Thickness Correction Trial แล้ว\n"
        "ทำงานบนสำเนา PTR_OVAL_STONE_SEAT_CONCEPT เท่านั้น ไม่แก้ต้นฉบับ ไม่ Union และไม่ Export\n"
        "รันสคริปต์ใน Rhino แล้วใช้ !cadseatthicknesscheck ตรวจผล\n"
        f"Report: {report_path}",
        file=__import__("discord").File(str(script_path)),
    )
