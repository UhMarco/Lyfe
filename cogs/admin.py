import discord, asyncio, utils.json, utils.functions
from discord.ext import commands
from classes.user import User
from classes.phrases import Phrases
phrases = Phrases()

def is_dev():
    def predictate(ctx):
        devs = utils.json.read_json("devs")
        if ctx.author.id in devs:
            return ctx.author.id
    return commands.check(predictate)

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        data = utils.json.read_json("blacklist")
        for item in data["blacklistedUsers"]:
            self.bot.blacklisted_users.append(item)

        try:
            data = utils.json.read_json("whitelist")
            for item in data["whitelist"]:
                self.bot.whitelisted.append(item)
        except Exception:
            pass
        print("+ Admin Cog loaded")

    @commands.command()
    @is_dev()
    async def lockdown(self, ctx):
        self.bot.lockdown = not self.bot.lockdown
        if self.bot.lockdown:
            await ctx.send("Lockdown initiated.")
        else:
            await ctx.send("Lockdown lifted.")

    @commands.command(aliases=['disconnect', 'stop', 's'])
    @is_dev()
    async def logout(self, ctx):
        if self.bot.maintenancemode:
            return

        if await utils.functions.confirm(ctx) is False:
            return await ctx.send("Aborted")

        await ctx.send("Stopping.")
        await self.bot.logout()


    @commands.command(aliases=['li', 'listitems', 'il'])
    @is_dev()
    async def itemlist(self, ctx, page=1):
        items = await utils.functions.getAllItems()
        embed = discord.Embed(title="**Item List**", color=discord.Color.purple())

        pagelimit = 5 * round(len(items) / 5)
        if pagelimit < len(items): pagelimit += 5
        pagelimit = int(pagelimit / 5)

        if page > pagelimit:
            if page == 1:
                return await ctx.send("Empty!")
            return await ctx.send("There aren't that many pages!")

        count = 0
        for item in items:
            item = items[item]
            count += 1
            if count > page * 5 - 5:
                name, desc, emoji, value, rarity = item["name"], item["description"], item["emoji"], item["value"], item["rarity"]
                embed.add_field(name=f"{emoji} {name}", value=f"**Description:** `{desc}`\n**Rarity:** `{rarity}`\n**Value:** $`{value}`", inline=False)

            if count == page * 5:
                break

        embed.set_footer(text=f"Item List | Page: {page}/{pagelimit}")
        await ctx.send(embed=embed)

    @commands.command(aliases=['si'])
    @is_dev()
    async def spawnitem(self, ctx, user: discord.Member, item):
        user = await User(user.id)
        if user.inventory is None: return await ctx.send(phrases.otherNoInventory)

        item = await utils.functions.getItem(item)
        if item is None: return await ctx.send(phrases.itemDoesNotExist)

        user.inventory.add(item)
        await user.update()
        name, emoji = item["name"], item["emoji"]
        await ctx.send(f"Given **{emoji} {name}** to **{user.discord.name}**.")

    @spawnitem.error
    async def spawnitem_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}spawnitem (item) (user)`")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send(phrases.userNotFound)


    @commands.command(aliases=['ri'])
    @is_dev()
    async def removeitem(self, ctx, user: discord.Member, item):
        user = await User(user.id)
        if user is None: return await ctx.send(phrases.userNotFound)
        if user.inventory is None: return await ctx.send(phrases.otherNoInventory)

        item = await utils.functions.getItem(item)
        if item is None: return await ctx.send(phrases.itemDoesNotExist)

        name, emoji = item["name"], item["emoji"]
        if not user.inventory.contains(item):
            return await ctx.send(f"**{user.discord.name}** doesn't have a **{emoji} {name}**.")

        user.inventory.remove(item)
        await user.update()
        await ctx.send(f"Removed **{emoji} {name}** from **{user.discord.name}**.")

    @removeitem.error
    async def removeitem_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}removeitem (item) (user)`")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send(phrases.userNotFound)


    @commands.command(aliases=['sb', 'setbal'])
    @is_dev()
    async def setbalance(self, ctx, user: discord.Member, amount):
        user = await User(user.id)
        if user is None: return await ctx.send(phrases.userNotFound)
        if user.inventory is None: return await ctx.send(phrases.otherNoInventory)

        try:
            amount = int(amount)
        except Exception:
            return await ctx.send("Enter a valid amount.")

        user.balance = amount
        await user.update()
        await ctx.send("Set **{}**'s balance to $`{:,}`".format(user.discord.name, amount))

    @setbalance.error
    async def setbalance_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}setbalance (user) (amount)`")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send(phrases.userNotFound)

    @commands.command(aliases=['setbankbal', 'sbb'])
    @is_dev()
    async def setbankbalance(self, ctx, user: discord.Member, amount):
        user = await User(user.id)
        if user is None: return await ctx.send(phrases.userNotFound)
        if user.inventory is None: return await ctx.send(phrases.otherNoInventory)

        try:
            amount = int(amount)
        except Exception:
            return await ctx.send("Enter a valid amount.")

        user.bank.balance = amount
        await user.update()
        await ctx.send("Set **{}**'s bank balance to $`{:,}`".format(user.discord.name, amount))

    @setbankbalance.error
    async def setbankbalance_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}setbankbalance (user) (amount)`")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send(phrases.userNotFound)


    @commands.command(aliases=['setbanklim', 'sbl'])
    @is_dev()
    async def setbanklimit(self, ctx, user: discord.Member, amount):
        user = await User(user.id)
        if user is None: return await ctx.send(phrases.userNotFound)
        if user.inventory is None: return await ctx.send(phrases.otherNoInventory)

        try:
            amount = int(amount)
        except Exception:
            return await ctx.send("Enter a valid amount.")

        user.bank.limit = amount
        await user.update()
        await ctx.send("Set **{}**'s bank limit to $`{:,}`".format(user.discord.name, amount))

    @setbanklimit.error
    async def setbanklimit_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}setbanklimit (user) (amount)`")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send(phrases.userNotFound)


    @commands.command(aliases=['reset'])
    @is_dev()
    async def resetdata(self, ctx, user):
        user = await User(user.id)
        if user is None: return await ctx.send(phrases.userNotFound)
        if user.inventory is None: return await ctx.send(phrases.otherNoInventory)

        if await utils.functions.confirm(ctx) is False:
            return await ctx.send("Aborted")

        message = await ctx.send(f"Resetting **{user.discord.name}'s** data... <a:loading:733746914109161542>")
        await user.setup()
        await message.edit(content=f"Resetting **{user.discord.name}'s** data... **Done!**")

    @resetdata.error
    async def resetdata_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}reset (user)`")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send(phrases.userNotFound)


    @commands.command()
    @is_dev()
    async def blacklist(self, ctx, member: discord.Member):
        if ctx.message.author.id == member.id:
            return await ctx.send("You can't blacklist yourself.")

        data = utils.json.read_json("blacklist")

        if member.id in data["blacklistedUsers"]:
            return await ctx.send("This user is already blacklisted.")

        data["blacklistedUsers"].append(member.id)
        self.bot.blacklisted_users.append(member.id)
        utils.json.write_json(data, "blacklist")
        await ctx.send(f"Blacklisted **{member.name}**.")
        print(f"{ctx.author} blacklisted {member}")

    @blacklist.error
    async def blacklist_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}blacklist (user)`")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send(phrases.userNotFound)


    @commands.command()
    @is_dev()
    async def unblacklist(self, ctx, member: discord.Member):
        data = utils.json.read_json("blacklist")

        if member.id not in data["blacklistedUsers"]:
            return await ctx.send("That user isn't blacklisted.")

        data["blacklistedUsers"].remove(member.id)
        self.bot.blacklisted_users.remove(member.id)
        utils.json.write_json(data, "blacklist")
        await ctx.send(f"Unblacklisted **{member.name}**.")
        print(f"{ctx.author} unblacklisted {member}")

    @unblacklist.error
    async def unblacklist_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}unblacklist (user)`")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send(phrases.userNotFound)


    @commands.command()
    @is_dev()
    async def whitelist(self, ctx, member: discord.Member):
        data = utils.json.read_json("whitelist")

        if member.id in data["whitelist"]:
            return await ctx.send("This user is already whitelisted.")

        data["whitelist"].append(member.id)
        self.bot.whitelisted.append(member.id)
        utils.json.write_json(data, "whitelist")
        await ctx.send(f"Whitelisted **{member.name}**.")

    @whitelist.error
    async def whitelist_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}whitelist (user)`")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send(phrases.userNotFound)


    @commands.command()
    @is_dev()
    async def unwhitelist(self, ctx, member: discord.Member):
        data = utils.json.read_json("whitelist")

        if member.id not in data["whitelist"]:
            return await ctx.send("That user isn't whitelisted.")

        data["whitelist"].remove(member.id)
        self.bot.whitelisted.remove(member.id)
        utils.json.write_json(data, "whitelist")
        await ctx.send(f"Unwhitelist **{member.name}**.")

    @unwhitelist.error
    async def unwhitelist_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}whitelist (user)`")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send(phrases.userNotFound)


    @commands.command()
    @is_dev()
    async def maintenance(self, ctx):
        self.bot.maintenancemode = not self.bot.maintenancemode
        await ctx.send(f"Maintenance-Mode set to **{self.bot.maintenancemode}**.")

def setup(bot):
    bot.add_cog(Admin(bot))
