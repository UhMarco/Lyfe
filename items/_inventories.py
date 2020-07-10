import discord, platform, datetime, logging, random
from discord.ext import commands
import platform, datetime

import cogs._json

robberytools = ['Gun', 'Hammer', 'Knife']

class Inventories(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("- Inventories Cog loaded")

    @commands.command(aliases=['li', 'listitems', 'il'])
    @commands.is_owner()
    async def itemlist(self, ctx, page=1):
        items = cogs._json.read_json("items")
        embed = discord.Embed(title="**Item List**", color=discord.Color.purple())

        pagelimit = 5 * round(len(items) / 5)
        if pagelimit < len(items): pagelimit += 5
        pagelimit = int(pagelimit / 5)

        if page > pagelimit:
            if page == 1:
                return await ctx.send("Your inventory is empty!")
            return await ctx.send("You don't have that many pages!")

        count = 0
        for item in items:
            item = items[item]
            count += 1
            if count > page * 5 - 5:
                name, desc, emoji, locked, value = item["name"], item["description"], item["emoji"], item["locked"], item["value"]
                embed.add_field(name=f"{emoji} {name}", value=f"**Description:** `{desc}`\n**Locked:** `{locked}`\n**Value:** $`{value}`", inline=False)

            if count == page * 5:
                break

        embed.set_footer(text=f"Item List | Page: {page}/{pagelimit}")
        await ctx.send(embed=embed)









    @commands.command(aliases=['inv'])
    async def inventory(self, ctx, page=1):
        data = cogs._json.read_json("inventories")
        items = cogs._json.read_json("items")
        bals = cogs._json.read_json("balances")

        if str(ctx.author.id) not in data:
            await ctx.send("It seems this is your first time checking your inventory, I'll give you a shopping cart and $`100` to get started!")
            item = items["shoppingcart"]
            del item["emoji"], item["value"]
            item["locked"] = False
            item["quantity"] = 1
            data.setdefault(str(ctx.author.id), []).append(item)
            bals[ctx.author.id] = 100
            cogs._json.write_json(data, "inventories")
            cogs._json.write_json(bals, "balances")

        items = cogs._json.read_json("items") # This is needed
        pagelimit = 5 * round(len(data[str(ctx.author.id)]) / 5)
        if pagelimit < len(data[str(ctx.author.id)]): pagelimit += 5
        pagelimit = int(pagelimit / 5)

        if page > pagelimit:
            if page == 1:
                return await ctx.send("Your inventory is empty!")
            return await ctx.send("You don't have that many pages!")

        bal = bals[str(ctx.author.id)]
        embed = discord.Embed(title=f":desktop: **{ctx.author.name}'s Inventory**", description=f"**Balance:** $`{bal}`", color=discord.Color.blue())
        count = 0
        for i in data[str(ctx.author.id)]:
            count += 1
            if count > page * 5 - 5:
                name, desc, locked, quantity = i["name"], i["description"], i["locked"], i["quantity"]
                emoji, value = items[name.replace(" ", "").lower()]["emoji"], items[name.replace(" ", "").lower()]["value"]
                embed.add_field(name=f"{emoji} {name}", value=f"**Description:** `{desc}`\n**Locked:** `{locked}`\n**Value:** $`{value}`\n**Quantity:** `{quantity}`", inline=False)

            if count == page * 5:
                break

        embed.set_footer(text=f"{ctx.author.id} | Page: {page}/{pagelimit}")
        await ctx.send(embed=embed)

    @commands.command(aliases=['invsee'])
    async def inventorysee(self, ctx, user: discord.Member, page=1):
        data = cogs._json.read_json("inventories")
        items = cogs._json.read_json("items")
        bals = cogs._json.read_json("balances")

        if str(user.id) not in data:
            return await ctx.send("This user hasn't initialized their inventory yet.")

        pagelimit = 5 * round(len(data[str(user.id)]) / 5)
        if pagelimit < len(data[str(user.id)]): pagelimit += 5
        pagelimit = int(pagelimit / 5)

        if page > pagelimit:
            if page == 1:
                return await ctx.send("Your inventory is empty!")
            return await ctx.send(f"**{user.name}** doesn't have that many pages!")

        bal = bals[str(user.id)]
        embed = discord.Embed(title=f":desktop: **{user.name}'s Inventory**", description=f"**Balance:** $`{bal}`", color=discord.Color.red())
        count = 0
        for i in data[str(user.id)]:
            count += 1
            if count > page * 5 - 5:
                name, desc, locked, quantity = i["name"], i["description"], i["locked"], i["quantity"]
                emoji, value = items[name.replace(" ", "").lower()]["emoji"], items[name.replace(" ", "").lower()]["value"]
                embed.add_field(name=f"{emoji} {name}", value=f"**Description:** `{desc}`\n**Locked:** `{locked}`\n**Value:** $`{value}`\n**Quantity:** `{quantity}`", inline=False)

            if count == page * 5:
                break

        embed.set_footer(text=f"{user.id} | Page: {page}/{pagelimit}")
        await ctx.send(embed=embed)

    @inventorysee.error
    async def inventorysee_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Usage: `.inventorysee (user) [page]`")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")

    @commands.command(aliases=['si'])
    @commands.is_owner()
    async def spawnitem(self, ctx, item, user: discord.Member):
        data = cogs._json.read_json("inventories")
        if str(user.id) not in data:
            return await ctx.send("This user hasn't initialized their inventory yet.")

        items = cogs._json.read_json("items")
        if item.lower() not in items:
            return await ctx.send("That item does not exist.")

        item = items[item.lower()]
        name, emoji = item["name"], item["emoji"]

        for i in data[str(user.id)]:
            if i["name"] == name:
                i["quantity"] += 1
                cogs._json.write_json(data, "inventories")
                return await ctx.send(f"Given **{emoji} {name}** to **{user.name}**")

        del item["emoji"], item["value"]
        item["locked"] = False
        item["quantity"] = 1
        data.setdefault(str(user.id), []).append(item)
        await ctx.send(f"Given **{emoji} {name}** to **{user.name}**.")
        cogs._json.write_json(data, "inventories")

    @spawnitem.error
    async def spawnitem_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Usage: `.spawnitem (item) (user)`")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")

    @commands.command(aliases=['ri'])
    @commands.is_owner()
    async def removeitem(self, ctx, item, user: discord.Member):
        data = cogs._json.read_json("inventories")
        if str(user.id) not in data:
            return await ctx.send("This user hasn't initialized their inventory yet.")

        if str(ctx.author.id) not in data:
            return await ctx.send("You haven't initialized your inventory yet.")

        items = cogs._json.read_json("items")
        if item.lower() not in items:
            return await ctx.send("That item does not exist.")

        item = items[item.lower()]
        name, emoji = item["name"], item["emoji"]
        change = False

        for i in data[str(user.id)]:
            if i["name"] == name:
                if i["quantity"] == 1:
                    data[str(user.id)].remove(i)
                    change = True
                else:
                    i["quantity"] -= 1
                    change = True
        if not change:
            return await ctx.send(f"**{user.name}** doesn't have a **{emoji} {name}**.")
        await ctx.send(f"Removed **{emoji} {name}** from **{user.name}**.")
        cogs._json.write_json(data, "inventories")

    @removeitem.error
    async def removeitem_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Usage: `.removeitem (item) (user)`")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")

    @commands.command(aliases=['ii', 'getinfo'])
    async def iteminfo(self, ctx, item):
        items = cogs._json.read_json("items")
        if item.lower() not in items:
            embed = discord.Embed(title="Item Doesn't Exist", color=discord.Colour.purple())
            return await ctx.send(embed=embed)
        item = items[item.lower()]

        name, desc, emoji, value = item["name"], item["description"], item["emoji"], item["value"]
        embed = discord.Embed(
            title=f"{emoji} **{name}**",
            description=f"**Description:** `{desc}`\n**Value:** $`{value}`",
            color=discord.Colour.purple()
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=['rob', 'burgle'])
    async def robbery(self, ctx, user: discord.Member, tool=None, item=None):
        if user.id == ctx.author.id:
            return await ctx.send("You can't rob yourself.")

        data = cogs._json.read_json("inventories")

        if str(ctx.author.id) not in data:
            return await ctx.send("You haven't initialized your inventory yet.")

        if str(user.id) not in data:
            return await ctx.send("This user hasn't initialized their inventory yet.")

        items = cogs._json.read_json("items")
        if not item:
            return await ctx.send("Usage: `.robbery [victim] [tool] [item]`")
        if item.lower() not in items:
            return await ctx.send("That item does not exist.")
        if tool.lower() not in items:
            return await ctx.send("That tool does not exist.")

        item = items[item.lower()]
        tool = items[tool.lower()]

        # Check if robber has the tool
        found = False
        for i in data[str(ctx.author.id)]:
            if i["name"] == tool["name"]:
                found = True
                break
        if not found:
            return await ctx.send("You don't have that tool in your inventory.")

        # Check if victim has the item
        found = False
        for i in data[str(user.id)]:
            if i["name"] == item["name"]:
                if i["locked"]:
                    emoji, name = item["emoji"], i["name"]
                    return await ctx.send(f"**{emoji} {name}** has been locked in **{user.name}**'s inventory.")
                found = True
                break
        if not found:
            emoji, name = item["emoji"], item["name"]
            return await ctx.send(f"**{user.name}** doesn't have **{emoji} {name}**.")

        # Robber's tool has been used
        for i in data[str(ctx.author.id)]:
            if i["name"] == tool["name"]:
                if i["quantity"] == 1:
                    data[str(ctx.author.id)].remove(i)
                else:
                    i["quantity"] -= 1

        # Check probability of successful robbery
        rand = random.randint(0, 100)
        chance = int(tool["description"][:3].strip("% "))

        toolname, itemname = tool["name"], item["name"]
        toolemoji, itememoji = items[toolname.replace(" ", "").lower()]["emoji"], items[itemname.replace(" ", "").lower()]["emoji"]

        if rand <= chance: # Success
            for i in data[str(user.id)]:
                if i["name"] == item["name"]:
                    if i["quantity"] == 1:
                        data[str(user.id)].remove(i)
                    else:
                        i["quantity"] -= 1

            given = False
            for i in data[str(ctx.author.id)]:
                if i["name"] == item["name"]:
                    i["quantity"] += 1
                    given = True

            if not given:
                del item["emoji"], item["value"]
                item["locked"] = False
                item["quantity"] = 1
                data.setdefault(str(ctx.author.id), []).append(item)

            embed = discord.Embed(
                title=f":moneybag: {ctx.author.name}'s robbery from {user.name}",
                description=f"**Robbery Succeeded**\n**{ctx.author.name}** gained **{itememoji} {itemname}**.\n**{ctx.author.name}** used **{toolemoji} {toolname}** to commit the robbery.\n**{user.name}** lost **{itememoji} {itemname}**.",
                color=discord.Color.green()
            )
            await ctx.send(embed = embed)

        else: # Fail
            embed = discord.Embed(
                title=f":moneybag: {ctx.author.name}'s robbery from {user.name}",
                description=f"**Robbery Failed**\n**{ctx.author.name}** lost **{toolemoji} {toolname}** while trying to steal **{itememoji} {itemname}** from **{user.name}**.",
                color=discord.Color.red()
            )
            await ctx.send(embed = embed)

        cogs._json.write_json(data, "inventories")

    @robbery.error
    async def robbery_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            data = cogs._json.read_json("inventories")
            items = cogs._json.read_json("items")
            if str(ctx.author.id) not in data:
                return await ctx.send("You haven't initialized your inventory yet.")

            embed = discord.Embed(title=f":hammer_pick: **{ctx.author.name}'s Robbery Tools**", color=discord.Color.blue())
            empty = True
            for i in data[str(ctx.author.id)]:
                name = i["name"]
                if any(ele in name for ele in robberytools):
                    desc, locked, quantity = i["description"], i["locked"], i["quantity"]
                    emoji, value = items[name.replace(" ", "").lower()]["emoji"], items[name.replace(" ", "").lower()]["value"]
                    embed.add_field(name=f"{emoji} {name}", value=f"**Description:** `{desc}`\n**Locked:** `{locked}`\n**Value:** $`{value}`\n**Quantity:** `{quantity}`", inline=False)
                    empty = False

            if empty:
                embed.add_field(name="You don't have any robbery tools!", value="`No robbing for you :(`", inline=False)
            embed.add_field(name="Usage:", value="`.robbery [victim] [tool] [item]`", inline=False)
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")


    @commands.command()
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def claim(self, ctx):
        items = cogs._json.read_json("items")
        data = cogs._json.read_json("inventories")
        if str(ctx.author.id) not in data:
            return await ctx.send("You haven't initialized your inventory yet.")

        rand = random.randint(1, len(items) - 1)

        c = 0
        confirm = False
        for item in items:
            item = items[item]
            c += 1
            if c == rand:
                daily = item
                confirm = True
                break

        if not confirm:
            return await ctx.send("Something went wrong.")

        name, emoji = daily["name"], daily["emoji"]

        given = False
        for i in data[str(ctx.author.id)]:
            if i["name"] == name:
                i["quantity"] += 1
                given = True

        if not given:
            del daily["emoji"], daily["value"]
            daily["locked"] = False
            daily["quantity"] = 1
            data.setdefault(str(ctx.author.id), []).append(daily)

        await ctx.send(f":mailbox_with_mail: You got **{emoji} {name}**.")
        cogs._json.write_json(data, "inventories")

    @claim.error
    async def claim_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            m, s = divmod(error.retry_after, 60)
            h, m = divmod(m, 60)
            if int(h) == 0 and int(m) == 0:
                await ctx.send(f':mailbox_with_no_mail: You must wait **{int(s)} seconds** to claim again.')
            elif int(h) == 0 and int(m) != 0:
                await ctx.send(f':mailbox_with_no_mail: You must wait **{int(m)} minutes and {int(s)} seconds** to claim again.')
            else:
                await ctx.send(f':mailbox_with_no_mail: You must wait **{int(h)} hours, {int(m)} minutes and {int(s)} seconds** to claim again.')
            return


    @commands.command()
    async def lock(self, ctx, item):
        items = cogs._json.read_json("items")
        data = cogs._json.read_json("inventories")
        if str(ctx.author.id) not in data:
            return await ctx.send("You haven't initialized your inventory yet.")
        if item.lower() not in items:
            return await ctx.send("That item does not exist.")

        # Check if a lock is owned
        found = False
        for i in data[str(ctx.author.id)]:
            if i["name"] == "Lock":
                found = True
                break
        if not found:
            return await ctx.send("You don't have **:lock: Lock** in your inventory.")

        # Check if you own the item
        name, emoji = items[item.replace(" ", "").lower()]["name"], items[item.replace(" ", "").lower()]["emoji"]
        found = False
        for i in data[str(ctx.author.id)]:
            if i["name"].replace(" ", "").lower() == item: # If found, check if locked.
                found = True
                if i["locked"]:
                    return await ctx.send(f"{emoji} {name} already locked.")
                else:
                    i["locked"] = True
                break
        if not found:
            return await ctx.send(f"You don't own a **{emoji} {name}**.")

        # Remove lock from inventory
        for i in data[str(ctx.author.id)]:
            if i["name"] == "Lock":
                if i["quantity"] == 1:
                    data[str(ctx.author.id)].remove(i)
                else:
                    i["quantity"] -= 1

        embed = discord.Embed(title=f"**{emoji} {name}** locked.\n**:lock: Lock** used.", color=discord.Color.blue())
        await ctx.send(embed=embed)
        cogs._json.write_json(data, "inventories")

    @lock.error
    async def lock_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send("Usage: `.lock (item)`")


    @commands.command()
    async def unlock(self, ctx, item):
        items = cogs._json.read_json("items")
        data = cogs._json.read_json("inventories")
        if str(ctx.author.id) not in data:
            return await ctx.send("You haven't initialized your inventory yet.")
        if item.lower() not in items:
            return await ctx.send("That item does not exist.")

        # Check if a unlock is owned
        found = False
        for i in data[str(ctx.author.id)]:
            if i["name"] == "Key":
                found = True
                break
        if not found:
            return await ctx.send("You don't have **:key: Key** in your inventory.")

        # Check if you own the item
        name, emoji = items[item.replace(" ", "").lower()]["name"], items[item.replace(" ", "").lower()]["emoji"]
        found = False
        for i in data[str(ctx.author.id)]:
            if i["name"].replace(" ", "").lower() == item: # If found, check if locked.
                found = True
                if not i["locked"]:
                    return await ctx.send(f"{emoji} {name} is not locked.")
                else:
                    i["locked"] = False
                break
        if not found:
            return await ctx.send(f"You don't own a **{emoji} {name}**.")

        # Remove lock from inventory
        for i in data[str(ctx.author.id)]:
            if i["name"] == "Key":
                if i["quantity"] == 1:
                    data[str(ctx.author.id)].remove(i)
                else:
                    i["quantity"] -= 1

        embed = discord.Embed(title=f"**{emoji} {name}** unlocked.\n**:key: Key** used.", color=discord.Color.blue())
        await ctx.send(embed=embed)
        cogs._json.write_json(data, "inventories")

    @unlock.error
    async def unlock_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send("Usage: `.unlock (item)`")

    @commands.command(aliases=['donate'])
    async def give(self, ctx, user: discord.Member, item):
        data = cogs._json.read_json("inventories")
        items = cogs._json.read_json("items")

        if str(ctx.author.id) not in data:
            return await ctx.send("You haven't initialized your inventory yet.")

        if str(user.id) not in data:
            return await ctx.send("This user hasn't initialized their inventory yet.")

        item = items[item]
        name, emoji = item["name"], item["emoji"]

        found = False
        for i in data[str(ctx.author.id)]:
            if i["name"] == name:
                if i["locked"]:
                    return await ctx.send(f"**{emoji} {name}** is locked in your inventory.")

                if i["quantity"] == 1:
                    data[str(ctx.author.id)].remove(i)
                else:
                    i["quantity"] -= 1

                found = True
                break

        if not found:
            return await ctx.send(f"You don't own a **{emoji} {name}**.")

        given = False
        for i in data[str(user.id)]:
            if i["name"] == name:
                i["quantity"] += 1
                given = True

        if not given:
            del item["emoji"], item["value"]
            item["locked"] = False
            item["quantity"] = 1
            data.setdefault(str(ctx.author.id), []).append(item)

        await ctx.send(f"**{emoji} {name}** transferred from **{ctx.author.name}** to **{user.name}**.")
        cogs._json.write_json(data, "inventories")

    @give.error
    async def give_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send("Usage: `.give (user) (item)`")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")

def setup(bot):
    bot.add_cog(Inventories(bot))
