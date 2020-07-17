import discord, platform, datetime, logging, random
from discord.ext import commands
import platform, datetime
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json

class Utilities(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("- Utilities Cog loaded")

    @commands.command()
    async def avatar(self, ctx, user:discord.Member):
        embed = discord.Embed(title=f"**{user.name}'s** Avatar", color=discord.Color.dark_blue())
        embed.set_image(url=user.avatar_url)
        await ctx.send(embed=embed)

    @avatar.error
    async def avatar_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title=f"**{ctx.author.name}'s** Avatar", color=discord.Color.dark_blue())
            embed.set_image(url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")

    @commands.command(name="8ball")
    async def _8Ball(self, ctx, *, question=None):
        if not question:
            return await ctx.send(":8ball: **8Ball:** Well that's cool but you actually have to ask something.")
        responses = ["Outlook unclear, try again later", "Sorry m8, try again", "mhm", "I don't know, you tell me", "lol", "Absolutely!", "Absolutely not!", "It's a yes from me", "It's a no from me", "Do what Jesus would do", "Nahhhh", "Sure I guess...", "It's plausible", "I don't think you'll like the answer...", "I think it's best I spare you of the truth."]
        wisdom = random.choice(responses)
        await ctx.send(f":8ball: **8Ball:** {wisdom}")


def setup(bot):
    bot.add_cog(Utilities(bot))
