"""PTR AI Discord bot entry point."""

import logging
import os

import discord
from discord.ext import commands

from commands.automation import automation_command
from commands.business import business_command
from commands.cadbrief import cadbrief_command
from commands.cadcheck import cadcheck_command
from commands.content import content_command
from commands.customer import customer_command
from commands.design import design_command
from commands.findcustomer import findcustomer_command
from commands.project import project_command
from commands.cadproduction import cadproduction_command
from commands.rhino import rhino_command
from commands.rhinoscript import rhinoscript_command
from commands.rhinoscript2 import rhinoscript2_command
from commands.rhinoscript3 import rhinoscript3_command
from commands.rhinoscript4 import rhinoscript4_command
from commands.veo import veo_command
from utils.config import load_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
LOGGER = logging.getLogger("ptr_ai")

COMMAND_HANDLERS = {
    "design": design_command,
    "cadbrief": cadbrief_command,
    "cadcheck": cadcheck_command,
    "cadproduction": cadproduction_command,
    "rhinoscript": rhinoscript_command,
    "rhinoscript2": rhinoscript2_command,
    "rhinoscript3": rhinoscript3_command,
    "rhinoscript4": rhinoscript4_command,
    "content": content_command,
    "business": business_command,
    "customer": customer_command,
    "findcustomer": findcustomer_command,
    "project": project_command,
    "veo": veo_command,
    "rhino": rhino_command,
    "automation": automation_command,
}


def build_bot() -> commands.Bot:
    """Create and configure the Discord bot."""
    config = load_config()
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix=config.command_prefix, intents=intents, help_command=None)
    bot.ptr_config = config  # type: ignore[attr-defined]

    @bot.event
    async def on_ready() -> None:
        LOGGER.info("PTR AI Agent logged in as %s", bot.user)

    @bot.command(name="help")
    async def help_command(ctx: commands.Context) -> None:
        command_list = "\n".join(f"!{name} <request>" for name in COMMAND_HANDLERS)
        await ctx.reply(
            "**PTR AI Jewelry Agent Commands**\n"
            f"{command_list}\n\n"
            "Flow: !cadbrief → !cadcheck → !rhinoscript → !rhinoscript2 → !rhinoscript3 → !rhinoscript4 → !cadproduction"
        )

    for command_name, handler in COMMAND_HANDLERS.items():
        bot.command(name=command_name)(handler)

    return bot


def main() -> None:
    """Load configuration and run the bot."""
    bot = build_bot()
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN is required. Copy .env.example to .env and set your token.")
    bot.run(token)


if __name__ == "__main__":
    main()
