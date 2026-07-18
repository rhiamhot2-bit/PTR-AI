"""PTR AI Discord bot entry point."""

import logging
import os

import discord
from discord.ext import commands

from commands.automation import automation_command
from commands.business import business_command
from commands.cadbrief import cadbrief_command
from commands.caduppercheck import caduppercheck_command
from commands.cadtiltshape import cadtiltshape_command
from commands.cadupperbridgetrial import cadupperbridgetrial_command
from commands.cadupperdistances import cadupperdistances_command
from commands.cadbridgeboolean import cadbridgeboolean_command
from commands.cadbridgecheck import cadbridgecheck_command
from commands.cadcheck import cadcheck_command
from commands.cadfullreadiness import cadfullreadiness_command
from commands.cadfinishingaudit import cadfinishingaudit_command
from commands.cadfinishingplan import cadfinishingplan_command
from commands.cadfullmetalboolean import cadfullmetalboolean_command
from commands.cadjoinplan import cadjoinplan_command
from commands.cadmetalbridgetrial import cadmetalbridgetrial_command
from commands.cadmetalcheck import cadmetalcheck_command
from commands.cadmetalgaps import cadmetalgaps_command
from commands.cadmetalrepairplan import cadmetalrepairplan_command
from commands.cadmetalrehearsal import cadmetalrehearsal_command
from commands.cadproduction import cadproduction_command
from commands.cadproductioncandidate import cadproductioncandidate_command
from commands.cadprong11boolean import cadprong11boolean_command
from commands.cadprong11check import cadprong11check_command
from commands.cadprong11trial import cadprong11trial_command
from commands.cadrepositionplan import cadrepositionplan_command
from commands.cadsupportcurveboolean import cadsupportcurveboolean_command
from commands.cadsupportcurvecheck import cadsupportcurvecheck_command
from commands.cadsupportcurvetrial import cadsupportcurvetrial_command
from commands.cadshoulderbuild import cadshoulderbuild_command
from commands.cadshouldercheck import cadshouldercheck_command
from commands.cadshoulderloft4 import cadshoulderloft4_command
from commands.cadshoulderplan import cadshoulderplan_command
from commands.content import content_command
from commands.customer import customer_command
from commands.design import design_command
from commands.findcustomer import findcustomer_command
from commands.project import project_command
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
    "cadmetalcheck": cadmetalcheck_command,
    "cadmetalrehearsal": cadmetalrehearsal_command,
    "cadmetalgaps": cadmetalgaps_command,
    "cadmetalrepairplan": cadmetalrepairplan_command,
    "cadmetalbridgetrial": cadmetalbridgetrial_command,
    "cadbridgecheck": cadbridgecheck_command,
    "cadbridgeboolean": cadbridgeboolean_command,
    "caduppercheck": caduppercheck_command,
    "cadupperdistances": cadupperdistances_command,
    "cadupperbridgetrial": cadupperbridgetrial_command,
    "cadrepositionplan": cadrepositionplan_command,
    "cadtiltshape": cadtiltshape_command,
    "cadprong11trial": cadprong11trial_command,
    "cadprong11check": cadprong11check_command,
    "cadprong11boolean": cadprong11boolean_command,
    "cadsupportcurvetrial": cadsupportcurvetrial_command,
    "cadsupportcurvecheck": cadsupportcurvecheck_command,
    "cadsupportcurveboolean": cadsupportcurveboolean_command,
    "cadfullmetalboolean": cadfullmetalboolean_command,
    "cadfullreadiness": cadfullreadiness_command,
    "cadfinishingaudit": cadfinishingaudit_command,
    "cadfinishingplan": cadfinishingplan_command,
    "cadproduction": cadproduction_command,
    "cadproductioncandidate": cadproductioncandidate_command,
    "cadjoinplan": cadjoinplan_command,
    "cadshoulderplan": cadshoulderplan_command,
    "cadshoulderbuild": cadshoulderbuild_command,
    "cadshouldercheck": cadshouldercheck_command,
    "cadshoulderloft4": cadshoulderloft4_command,
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
    config = load_config()
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix=config.command_prefix, intents=intents, help_command=None)
    bot.ptr_config = config

    @bot.event
    async def on_ready() -> None:
        LOGGER.info("PTR AI Agent logged in as %s", bot.user)

    @bot.command(name="help")
    async def help_command(ctx: commands.Context) -> None:
        command_list = "\n".join(f"!{name} <request>" for name in COMMAND_HANDLERS)
        await ctx.reply(
            "**PTR AI Jewelry Agent Commands**\n"
            f"{command_list}\n\n"
            "Flow: !cadbrief → !cadcheck → !rhinoscript → !rhinoscript2 → "
            "!rhinoscript3 → !rhinoscript4 → !cadproduction → !cadjoinplan → "
            "!cadshoulderplan → !cadshoulderbuild → !cadshoulderloft4 → "
            "!cadshouldercheck → !cadmetalcheck → !cadmetalrehearsal → "
            "!cadmetalgaps → !cadmetalrepairplan → !cadmetalbridgetrial → !cadbridgecheck → !cadbridgeboolean → !caduppercheck → !cadupperdistances → !cadupperbridgetrial → !cadrepositionplan → !cadtiltshape → !cadprong11trial → !cadprong11check → !cadprong11boolean → !cadsupportcurvetrial → !cadsupportcurvecheck → !cadsupportcurveboolean → !cadfullmetalboolean → !cadfullreadiness → !cadproductioncandidate → !cadfinishingaudit → !cadfinishingplan"
        )

    for command_name, handler in COMMAND_HANDLERS.items():
        bot.command(name=command_name)(handler)
    return bot

def main() -> None:
    bot = build_bot()
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN is required. Copy .env.example to .env and set your token.")
    bot.run(token)

if __name__ == "__main__":
    main()
