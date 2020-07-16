import discord, random, datetime
from discord.ext import commands

class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("- Events Cog loaded")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Ignored errors
        ignored = (commands.CommandNotFound, commands.MissingRequiredArgument, commands.BadArgument)#, commands.UserInputError
        if isinstance(error, ignored):
            return

        # Error handling
        if isinstance(error, commands.CommandOnCooldown):
            if ctx.message.content == f"{self.bot.prefix}claim":
                return
            m, s = divmod(error.retry_after, 60)
            h, m = divmod(m, 60)
            if int(h) == 0 and int(m) == 0:
                await ctx.send(f':stopwatch: You must wait **{int(s)} seconds** to use this command again.')
            elif int(h) == 0 and int(m) != 0:
                await ctx.send(f':stopwatch: You must wait **{int(m)} minutes and {int(s)} seconds** to use this command again.')
            else:
                await ctx.send(f':stopwatch: You must wait **{int(h)} hours, {int(m)} minutes and {int(s)} seconds** to use this command again.')
            return

        elif isinstance(error, commands.CheckFailure):
            return await ctx.send("Insufficient permissions.")

        elif isinstance(error, commands.CommandInvokeError):
            embed = discord.Embed(title=":x:  **I ran into a problem!**", description="This is likely due to missing permissions.\nIf you believe this was an error, please [report it](https://discord.gg/zAZ3vKJ).", color=discord.Color.red())
            await ctx.send(embed=embed)
            return print(f"\n===============================================\nReplied in ctx\nError: {error}\n{ctx.author}: {ctx.message.content}\n===============================================\n")


        print("\n----------\n")
        raise error
        print("\n----------\n")

def setup(bot):
    bot.add_cog(Events(bot))
