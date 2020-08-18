import discord, random, datetime, asyncio
from discord.ext import commands
import utils.json

class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("- Events Cog loaded")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print(f"JOINED {guild.name} - Owner: {guild.owner} - Members: {len(guild.members)} - Now in {len(self.bot.guilds)} guilds.")
        await self.bot.change_presence(activity=discord.Game(name=f"{self.bot.prefix}help in {len(self.bot.guilds)} servers"))

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        print(f"LEFT {guild.name} - Owner: {guild.owner} - Members: {len(guild.members)} - Now in {len(self.bot.guilds)} guilds.")
        await self.bot.change_presence(activity=discord.Game(name=f"{self.bot.prefix}help in {len(self.bot.guilds)} servers"))

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        self.bot.errors += 1
        # Ignored errors
        ignored = (commands.CommandNotFound, commands.MissingRequiredArgument, commands.BadArgument)#, commands.UserInputError
        if isinstance(error, ignored):
            return

        # Error handling
        if isinstance(error, commands.CommandOnCooldown):
            if f"{self.bot.prefix}claim" in ctx.message.content or f"{self.bot.prefix}work" in ctx.message.content:
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
            if str(error.original) == "403 Forbidden (error code: 50013): Missing Permissions":
                try:
                    embed = discord.Embed(title=":x: **Missing Permissions**", description="If you believe this was an error, please [report it](https://discord.gg/zAZ3vKJ).", color=discord.Color.red())
                    await ctx.send(embed=embed)
                    print(f"\n===============================================\nMISSING PERMISSIONS\nReplied in ctx\nError: {error}\n{ctx.author}: {ctx.message.content}\n===============================================\n")
                except Exception:
                    pass
            else:
                self.bot.important_errors += 1
                embed = discord.Embed(title=":x:  **I found an error!**", description="If you wish, you may [report it](https://discord.gg/zAZ3vKJ).", color=discord.Color.red())
                await ctx.send(embed=embed)
                print(f"\n===============================================\nCOMMAND INVOKE ERROR\nReplied in ctx\nError: {error}\n{ctx.author}: {ctx.message.content}\n===============================================\nRAISING ERROR:")
                raise error
            return

        elif isinstance(error, commands.UnexpectedQuoteError) or isinstance(error, commands.ExpectedClosingQuoteError):
            embed = discord.Embed(title=":x: **Unexpected Quote**", description="There was an unexpected quote in your command.\nIf you think this is a mistake, you may [report it](https://discord.gg/zAZ3vKJ).", color=discord.Color.red())
            await ctx.send(embed=embed)
            print(f"\n===============================================\nUNEXPECTED QUOTE\nReplied in ctx\nError: {error}\n{ctx.author}: {ctx.message.content}\n===============================================\n")
            return

        self.bot.important_errors += 1
        print("\n----------\n")
        raise error
        print("\n----------\n")

    @commands.Cog.listener()
    async def on_guild_join(guild):
        general = find(lambda x: x.name == 'general',  guild.text_channels)
        if general and general.permissions_for(guild.me).send_messages:
        welcomebed = discord.Embed(
            title="Thank you for inviting me!",
            description=f"A few things about myself: \n \nMy prefix is `{self.bot.prefix}`\nYou can find help by doing `{self.bot.prefix}help`\nYou can join the support server by doing `{self.bot.prefix}invite`\nTo start your epic adventure, do `{self.bot.prefix}inv`",
            color=discord.Color.green()
        )
        welcomebed.set_thumbnail(url=self.bot.user.avatar_url)
        return await ctx.send(embed=welcomebed)

def setup(bot):
    bot.add_cog(Events(bot))
