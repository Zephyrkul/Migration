import os
import discord
from discord.ext import commands

from .utils import checks
from .utils.dataIO import dataIO


class Migration:
    def __init__(self, bot):
        self.bot = bot
        self.old_on_message = bot.on_message
        self.data = dataIO.load_json("data/migration/settings.json")
        bot.remove_listener(bot.on_message)
        bot.on_message = None

    def __unload(self):
        self.bot.on_message = self.old_on_message

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def yieldto(self, ctx, *, bot: discord.Member):
        if not bot.bot:
            return await self.bot.say("{} is not a bot!".format(bot))
        self.data["V3"] = bot.id
        dataIO.save_json("data/migration/settings.json", self.data)
        await self.bot.say((
            "I will no longer respond to commands if {} is online.\n"
            "Unload this cog to listen to commands again."
        ).format(bot.mention))

    async def on_message(self, message):
        if message.author.bot:
            return
        if message.server is None or "unload migration" in message.content:
            return await self.old_on_message(message)
        red_v3 = message.server.get_member(self.data.get("V3"))
        if red_v3 and red_v3.status != discord.Status.offline:
            return
        return await self.old_on_message(message)

def _check_folders():
    fol = "data/migration"
    if not os.path.exists(fol):
        print("Creating {} folder...".format(fol))
        os.makedirs(fol)


def _check_files():
    fil = "data/migration/settings.json"
    if not dataIO.is_valid_json(fil):
        print("Creating default {}...".format(fil))
        dataIO.save_json(fil, {})


def setup(bot):
    _check_folders()
    _check_files()
    bot.add_cog(Migration(bot))
