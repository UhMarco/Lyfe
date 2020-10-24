import discord, random, asyncio
from discord.ext import commands
import utils.json

import utils.functions
from classes.user import User
from classes.phrases import Phrases
phrases = Phrases()

robberytools = ["knife", "gun", "hammer"]

class Crime(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("+ Crime Cog loaded")

    @commands.command(aliases=['rob', 'burgle'])
    async def robbery(self, ctx, user: discord.Member, tool, item):
        author = await User(ctx.author.id)
        if author.inventory is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(phrases.noInventory)

        user = await User(user.id)
        if not user:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(phrases.userNotFound)
        if user.inventory is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(phrases.otherNoInventory)

        if user.discord.id == ctx.author.id:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("You can't rob yourself.")

        # Check if items exist
        item = await utils.functions.getItem(item)
        if item is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(phrases.itemDoesNotExist)

        tool = await utils.functions.getItem(tool)
        if item is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(phrases.itemDoesNotExist)

        # Check if the entered tool is allowed
        if tool["name"].lower() not in robberytools:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("That is not a valid tool.")

        # Check if robber has the tool
        if not author.inventory.contains(tool):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("You don't have that tool in your inventory.")

        emoji, name = item["emoji"], item["name"]
        # Check if victim has the item
        if not user.inventory.contains(item):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**{user.discord.name}** doesn't have **{emoji} {name}**.")

        # Check if item is locked
        if user.inventory.get(item)["locked"]:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**{emoji} {name}** is locked in **{user.discord.name}'s** inventory.")

        # Robber's tool has been used
        author.inventory.remove(tool)

        # Check probability of successful robbery
        rand = random.randint(0, 100)
        chance = int(tool["description"][:3].strip("% "))

        toolname, itemname = tool["name"], item["name"]
        toolemoji, itememoji = tool["emoji"], item["emoji"]

        if rand <= chance: # Success
            user.inventory.remove(item)
            author.inventory.add(item)

            embed = discord.Embed(
                title=f":moneybag: {ctx.author.name}'s robbery from {user.discord.name}",
                description=f"**Robbery Succeeded**\n**{ctx.author.name}** gained **{itememoji} {itemname}** from **{user.discord.name}**.\n**{ctx.author.name}** used **{toolemoji} {toolname}** to commit the robbery.",
                color=discord.Color.green()
            )
            await ctx.send(embed = embed)
            try:
                embed = discord.Embed(
                    title=f":moneybag: {ctx.author.name} has robbed you!",
                    description=f"**Robbery Succeeded**\n**{ctx.author.name}** gained **{itememoji} {itemname}** from **{user.discord.name}**.\n**{ctx.author.name}** used **{toolemoji} {toolname}** to commit the robbery.",
                    color=discord.Color.red()
                )
                await user.discord.send(embed=embed)
            except discord.Forbidden:
                pass

        else: # Fail
            failureReasons = utils.json.read_json("robbery")
            failureReason = random.choice(failureReasons["failureReasons"])
            embed = discord.Embed(
                title=f":moneybag: {ctx.author.name}'s robbery from {user.discord.name}",
                description=f"{failureReason}\n**{ctx.author.name}** lost **{toolemoji} {toolname}** while trying to steal **{itememoji} {itemname}** from **{user.discord.name}**.",
                color=discord.Color.red()
            )
            await ctx.send(embed = embed)
            try:
                embed = discord.Embed(
                    title=f":moneybag: {ctx.author.name} attempted to rob you!",
                    description=f"{failureReason}\n**{ctx.author.name}** lost **{toolemoji} {toolname}** while trying to steal **{itememoji} {itemname}** from **{user.discord.name}**.",
                    color=discord.Color.green()
                )
                await user.discord.send(embed=embed)
            except discord.Forbidden:
                pass

        await user.update()
        await author.update()

    @robbery.error
    async def robbery_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            user = await User(ctx.author.id)
            if user.inventory is None: return await ctx.send(phrases.noInventory)

            embed = discord.Embed(title=f":hammer_pick: **{ctx.author.name}'s Robbery Tools**", color=discord.Color.blue())
            empty = True
            for i in user.inventory:
                name = i["name"]
                if any(ele in name.lower() for ele in robberytools):
                    locked, quantity = i["locked"], i["quantity"]
                    item = await utils.functions.getItem(name)
                    desc, emoji, value = item["description"], item["emoji"], item["value"]
                    embed.add_field(name=f"{emoji} {name}", value=f"**Description:** `{desc}`\n**Locked:** `{locked}`\n**Value:** $`{value}`\n**Quantity:** `{quantity}`", inline=False)
                    empty = False

            if empty:
                embed.add_field(name="You don't have any robbery tools!", value="`No robbing for you :(`", inline=False)

            embed.add_field(name="Usage:", value=f"`{self.bot.prefix}robbery (victim) (tool) (item)`", inline=False)
            return await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 900, commands.BucketType.user)
    async def dynamite(self, ctx, user: discord.Member):
        user = await User(user.id)
        if not user:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(phrases.userNotFound)
        if user.inventory is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(phrases.otherNoInventory)

        author = await User(ctx.author.id)
        if author.inventory is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(phrases.noInventory)

        if not author.inventory.contains(await utils.functions.getItem("dynamite")):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("You don't have a :firecracker: **Dynamite** in your inventory.")

        author.inventory.remove(await utils.functions.getItem("dynamite"))

        if user.discord == ctx.author:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("Consider yourself blown up. I'm not actually going to do anything though.")

        if user.balance < 10:
            if user.bank.balance == 0:
                ctx.command.reset_cooldown(ctx)
                return await ctx.send(f"**{user.discord.name}** is incredibly poor, leave them alone will ya?")
            else:
                ctx.command.reset_cooldown(ctx)
                return await ctx.send(f"**{user.discord.name}** doesn't have enough money in their inventory for you to blow up. Maybe check their bank account :smirk:")

        originalbalance = user.balance
        user.balance = int(user.balance * 0.8)

        await ctx.send(":firecracker: You blew up $`{:,}` of **{}'s** money.".format(int(originalbalance * 0.2), user.discord.name))
        await user.update()
        await author.update()
        try:
            await user.discord.send("**{}** blew up $`{:,}` of your money!".format(ctx.author, int(originalbalance * 0.2)))
        except discord.Forbidden:
            pass

    @dynamite.error
    async def dynamite_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"Usage: `{self.bot.prefix}dynamite (user)`")


    @commands.command()
    @commands.cooldown(1, 900, commands.BucketType.user)
    async def bomb(self, ctx, user: discord.Member):
        user = await User(user.id)
        if not user:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(phrases.userNotFound)
        if user.inventory is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(phrases.otherNoInventory)

        author = await User(ctx.author.id)
        if author.inventory is None: return await ctx.send(phrases.noInventory)

        if not author.inventory.contains(await utils.functions.getItem("bomb")):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("You don't have a :bomb: **Bomb** in your inventory.")

        author.inventory.remove(await utils.functions.getItem("bomb"))

        if user.discord == ctx.author:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("Consider yourself blown up. I'm not actually going to do anything though.")

        if user.bank.balance < 10:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**{user.name}** is incredibly poor, leave them alone will ya?")

        originalbalance = user.bank.balance
        user.bank.balance = int(user.bank.balance * 0.9)

        await ctx.send(":bomb: You blew up $`{:,}` of **{}'s** money in their bank.".format(int(originalbalance * 0.1), user.discord.name))
        await user.update()
        await author.update()
        try:
            await user.discord.send("**{}** blew up $`{:,}` of your money in your bank!".format(ctx.author, int(originalbalance * 0.1)))
        except discord.Forbidden:
            pass

    @bomb.error
    async def bomb_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"Usage: `{self.bot.prefix}bomb (user)`")

    @commands.command()
    @commands.cooldown(1, 900, commands.BucketType.user)
    async def axe(self, ctx, user: discord.Member, *, item):
        user = await User(user.id)
        if user is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(phrases.userNotFound)
        if user.inventory is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(phrases.otherNoInventory)

        author = await User(ctx.author.id)
        if author.inventory is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(phrases.noInventory)

        if ctx.author == user.discord:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("You can't do that to yourself.")

        if not author.inventory.contains(await utils.functions.getItem("axe")):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("An :axe: **Axe** is required for this.")

        author.inventory.remove(await utils.functions.getItem("axe"))

        item = await utils.functions.getItem(item)
        if item is None: return await ctx.send(phrases.itemDoesNotExist)
        name, emoji = item["name"], item["emoji"]

        if not user.inventory.contains(item):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**{user.discord.name}** doesn't have {emoji} **{name}** in their inventory.")

        if not user.inventory.get(item)["locked"]:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"{emoji} **{name}** is not locked in **{user.discord.name}'s** inventory.")

        user.inventory.get(item)["locked"] = False

        if random.randint(0, 100) > 25:
            await user.update()
            await ctx.send(f"Unlocked {emoji} **{name}** in **{user.discord.name}'s** inventory.")
            try:
                await user.discord.send(f"Heads up! **{ctx.author.name}** unlocked {emoji} **{name}** in your inventory.")
            except discord.Forbidden:
                pass
        else:
            await ctx.send(f"Unlocking failed! You lost your {emoji} **{name}**")

        await author.upate()

    @axe.error
    async def axe_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"Usage: `{self.bot.prefix}axe (user) (item)`")


    @commands.command()
    @commands.cooldown(1, 900, commands.BucketType.user)
    async def burn(self, ctx, user: discord.Member, item):
        user = await User(user.id)
        if user is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(phrases.userNotFound)
        if user.inventory is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(phrases.otherNoInventory)

        author = await User(ctx.author.id)
        if author.inventory is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(phrases.noInventory)

        if ctx.author == user.discord:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("You can't do that to yourself.")

        if not author.inventory.contains(await utils.functions.getItem("fire")):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(":fire: **Fire** is required for this.")

        item = await utils.functions.getItem(item)
        if item is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(phrases.itemDoesNotExist)
        name, emoji = item["name"], item["emoji"]

        if not user.inventory.contains(item):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**{user.discord.name}** doesn't have {emoji} **{name}** in their inventory.")

        if name == "Dragon" or name == "Evolved Dragon":
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("Let me stop you right there- Dragons are fireproof.")
        if name == "Fire Extinguisher" or name == "Dragon" or name == "Evolved Dragon":
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("You cannot burn this item.")

        author.inventory.remove(await utils.functions.getItem("fire"))

        if user.inventory.contains(await utils.functions.getItem("fireextinguisher")):
            try:
                await user.discord.send(f"**{ctx.author}** tried to burn your **{name}** but you extinguised the fire costing **1 :fire_extinguisher: Fire extinguisher**")
            except discord.Forbidden:
                pass
            await ctx.send(f"**{user.discord.name}** had a **:fire_extinguisher: Fire Extinguisher** and the flames were put out!")
            user.inventory.remove(await utils.functions.getItem("fireextinguisher"))

        else:
            user.inventory.remove(item)

            await ctx.send(f":fire: You burned **{user.discord.name}'s {emoji} {name}**")
            try:
                    await user.discord.send(f"**{ctx.author}** burned your {emoji} **{name}**")
            except discord.Forbidden:
                pass

        await author.update()
        await user.update()

    @burn.error
    async def burn_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"Usage: `{self.bot.prefix}burn (user) (item)`")

def setup(bot):
    bot.add_cog(Crime(bot))
