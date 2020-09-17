import discord, platform, logging, random, os, time, asyncio
from discord.ext import commands
import platform
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json
from tabulate import tabulate

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

        await ctx.send("Please confirm.")
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author
        message = await self.bot.wait_for('message', check=check)
        if message.content.lower() == "confirm" or message.content.lower() == "yes":
            pass
        else:
            return await ctx.send("Aborted.")

        await ctx.send("Stopping.")
        await self.bot.logout()


    @commands.command(aliases=['li', 'listitems', 'il'])
    @is_dev()
    async def itemlist(self, ctx, page=1):
        items = await self.bot.items.find("items")
        items = items["items"]
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


    @commands.command(aliases=['si', 'gi'])
    @is_dev()
    async def spawnitem(self, ctx, item, user):
        if len(ctx.message.mentions) == 0:
            try:
                user = self.bot.get_user(int(user))
                if user is None:
                    return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
            except ValueError:
                return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
        else:
            user = ctx.message.mentions[0]

        data = await self.bot.inventories.find(user.id)
        if data is None:
            return await ctx.send("This user hasn't initialized their inventory yet.")

        items = await self.bot.items.find("items")
        items = items["items"]
        if item.lower() not in items:
            return await ctx.send("That item does not exist.")

        inventory = data["inventory"]
        item = items[item.lower()]
        name, emoji = item["name"], item["emoji"]

        found = False
        for i in inventory:
            if i["name"] == name:
                i["quantity"] += 1
                found = True

        if not found:
            del item["emoji"], item["value"], item["description"], item["rarity"]
            item["locked"] = False
            item["quantity"] = 1
            inventory.append(item)
        await ctx.send(f"Given **{emoji} {name}** to **{user.name}**.")
        await self.bot.inventories.upsert({"_id": user.id, "inventory": inventory})

    @spawnitem.error
    async def spawnitem_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}spawnitem (item) (user)`")


    @commands.command(aliases=['ri'])
    @is_dev()
    async def removeitem(self, ctx, item, user):
        if len(ctx.message.mentions) == 0:
            try:
                user = self.bot.get_user(int(user))
                if user is None:
                    return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
            except ValueError:
                return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
        else:
            user = ctx.message.mentions[0]

        data = await self.bot.inventories.find(user.id)
        if data is None:
            return await ctx.send("This user hasn't initialized their inventory yet.")

        items = await self.bot.items.find("items")
        items = items["items"]
        if item.lower() not in items:
            return await ctx.send("That item does not exist.")

        inventory = data["inventory"]
        item = items[item.lower()]
        name, emoji = item["name"], item["emoji"]

        change = False
        for i in inventory:
            if i["name"] == name:
                if i["quantity"] == 1:
                    inventory.remove(i)
                    change = True
                else:
                    i["quantity"] -= 1
                    change = True
        if not change:
            return await ctx.send(f"**{user.name}** doesn't have a **{emoji} {name}**.")
        await ctx.send(f"Removed **{emoji} {name}** from **{user.name}**.")
        await self.bot.inventories.upsert({"_id": user.id, "inventory": inventory})

    @removeitem.error
    async def removeitem_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}removeitem (item) (user)`")


    @commands.command(aliases=['sb'])
    @is_dev()
    async def setbalance(self, ctx, user, amount="n"):
        if len(ctx.message.mentions) == 0:
            try:
                user = self.bot.get_user(int(user))
                if user is None:
                    return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
            except ValueError:
                return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
        else:
            user = ctx.message.mentions[0]

        data = await self.bot.inventories.find(user.id)
        if data is None:
            return await ctx.send("This user hasn't initialized their inventory yet.")

        try:
            amount = int(amount)
        except Exception:
            return await ctx.send("Enter a valid amount")

        await self.bot.inventories.upsert({"_id": user.id, "balance": amount})
        await ctx.send(f"Set **{user.name}'s** balance to $`{amount}`")

    @setbalance.error
    async def setbalance_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}setbalance (user) (amount)`")


    @commands.command(aliases=['reset'])
    @is_dev()
    async def resetdata(self, ctx, user):
        if len(ctx.message.mentions) == 0:
            try:
                user = self.bot.get_user(int(user))
                if user is None:
                    return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
            except ValueError:
                return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
        else:
            user = ctx.message.mentions[0]

        await ctx.send("Please confirm.")
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author
        message = await self.bot.wait_for('message', check=check)
        if message.content.lower() == "confirm" or message.content.lower() == "yes":
            pass
        else:
            return await ctx.send("Aborted.")

        items = await self.bot.items.find("items")
        items = items["items"]
        data = []
        message = await ctx.send(f"Resetting **{user.name}'s** data... <a:loading:733746914109161542>")
        item = items["shoppingcart"]
        del item["emoji"], item["value"], item["description"], item["rarity"]
        item["locked"] = False
        item["quantity"] = 1
        data.append(item)
        await self.bot.inventories.upsert({"_id": user.id, "balance": 100})
        await self.bot.inventories.upsert({"_id": user.id, "bankbalance": 0})
        await self.bot.inventories.upsert({"_id": user.id, "banklimit": 0})
        await self.bot.inventories.upsert({"_id": user.id, "job": None})
        await self.bot.inventories.upsert({"_id": user.id, "inventory": data})
        await self.bot.inventories.upsert({"_id": user.id, "titles": []})
        await message.edit(content=f"Resetting **{user.name}'s** data... **Done!**")

    @resetdata.error
    async def resetdata_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}reset (user)`")


    @commands.command()
    @is_dev()
    async def blacklist(self, ctx, member):
        if len(ctx.message.mentions) == 0:
            try:
                member = self.bot.get_user(int(member))
                if member is None:
                    return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
            except ValueError:
                return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
        else:
            member = ctx.message.mentions[0]

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


    @commands.command()
    @is_dev()
    async def unblacklist(self, ctx, member):
        if len(ctx.message.mentions) == 0:
            try:
                member = self.bot.get_user(int(member))
                if member is None:
                    return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
            except ValueError:
                return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
        else:
            member = ctx.message.mentions[0]

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


    @commands.command()
    @is_dev()
    async def whitelist(self, ctx, member):
        if len(ctx.message.mentions) == 0:
            try:
                member = self.bot.get_user(int(member))
                if member is None:
                    return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
            except ValueError:
                return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
        else:
            member = ctx.message.mentions[0]

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


    @commands.command()
    @is_dev()
    async def unwhitelist(self, ctx, member):
        if len(ctx.message.mentions) == 0:
            try:
                member = self.bot.get_user(int(member))
                if member is None:
                    return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
            except ValueError:
                return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
        else:
            member = ctx.message.mentions[0]

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


    @commands.command()
    @is_dev()
    async def load(self, ctx, module):
        if self.bot.maintenancemode:
            return

        try:
            self.bot.load_extension(f"cogs.{module.lower()}")
            name = module.lower()
            return await ctx.send(f"**{name[:1].upper()}{name[1:]}** has been loaded.")
        except Exception as e:
            return await ctx.send(e)

    @load.error
    async def load_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}load (module)`")


    @commands.command()
    @is_dev()
    async def reload(self, ctx, module):
        if self.bot.maintenancemode:
            return
        if module == "all":
            start = time.time()
            for file in os.listdir(cwd+"/cogs"):
                if file.endswith(".py") and not file.startswith("_"):
                    self.bot.reload_extension(f"cogs.{file[:-3]}")
                    name = file[:-3].lower()

            end = time.time()
            return await ctx.send("Operation took: `{:.5f}` seconds".format(end - start))
        try:
            self.bot.reload_extension(f"cogs.{module.lower()}")
            name = module.lower()
            return await ctx.send(f"**{name[:1].upper()}{name[1:]}** has been reloaded.")
        except Exception as e:
            return await ctx.send(e)

    @reload.error
    async def reload_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}reload (module/all)`")


    @commands.command()
    @is_dev()
    async def unload(self, ctx, module):
        if self.bot.maintenancemode:
            return
        if module.lower() == "admin":
            return await ctx.send("That's not a good idea...")

        try:
            self.bot.unload_extension(f"cogs.{module.lower()}")
            name = module.lower()
            return await ctx.send(f"**{name[:1].upper()}{name[1:]}** has been unloaded.")
        except Exception as e:
            return await ctx.send(e)

    @unload.error
    async def unload_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}unload (module)`")


    @commands.command()
    @is_dev()
    async def maintenance(self, ctx):
        self.bot.maintenancemode = not self.bot.maintenancemode
        await ctx.send(f"Maintenance-Mode set to **{self.bot.maintenancemode}**.")


    @commands.command()
    @is_dev()
    async def addbeta(self, ctx, user):
        await ctx.send("Please confirm.")
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author
        message = await self.bot.wait_for('message', check=check)
        if message.content.lower() == "confirm" or message.content.lower() == "yes":
            pass
        else:
            return await ctx.send("Aborted.")

        if user == "all":
            data = await self.bot.inventories.get_all()
            for i in data:
                await self.bot.inventories.upsert({"_id": i["_id"], "beta": True})
            return await ctx.send("All current players now have beta.")

        elif len(ctx.message.mentions) == 0:
            try:
                user = self.bot.get_user(int(user))
                if user is None:
                    return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
            except ValueError:
                return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
        else:
            user = ctx.message.mentions[0]

        if await self.bot.inventories.find(user.id) is None:
            return await ctx.send("Inv not init.")
        await self.bot.inventories.upsert({"_id": user.id, "beta": True})
        await ctx.send(f"**{user.name}** given beta.")

def setup(bot):
    bot.add_cog(Admin(bot))
