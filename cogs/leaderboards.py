import discord, platform, logging, random, os, asyncio
from discord.ext import commands
import platform
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json
from tabulate import tabulate
from datetime import datetime

def is_dev():
    def predictate(ctx):
        devs = utils.json.read_json("devs")
        if any(ctx.author.id for ele in devs):
            return ctx.author.id
    return commands.check(predictate)

class Leaderboards(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("+ Leaderboards Cog loaded")

    @commands.command(aliases=['leaderboards', 'lb'])
    async def leaderboard(self, ctx):
        data = await self.bot.inventories.get_all()
        items = await self.bot.items.find("items")
        items = items["items"]
        all = []
        for i in data:
            inv = i["inventory"]
            value = 0
            for x in inv:
                value += x["quantity"] * items[x["name"].replace(" ", "").lower()]["value"]
            total = i["balance"] + i["bankbalance"] + value
            all.append({"id": i['_id'], "total": total})

        sort = sorted(all, key=lambda k: k['total'], reverse=True)
        places = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th']
        entries = []
        count = 0
        for i in sort:
            try:
                user = self.bot.get_user(i['id'])
                if user is None:
                    count -= 1
                else:
                    entries.append([places[count], user.name, f"${i['total']}"])
            except (KeyError, IndexError):
                entries.append([places[count], "Invalid User", f"${0}"])
            count += 1
            if count == 10:
                break

        output = ("```" + tabulate(entries, tablefmt="simple", headers=["#", "Player", "Total Value"]) + "```")
        embed = discord.Embed(title=":trophy:  Total Leaderboard:", description=output, color=discord.Color.gold())
        await ctx.send(embed=embed)

    @commands.command(aliases=['balancetop'])
    async def baltop(self, ctx):
        data = await self.bot.inventories.get_all()

        data = sorted(data, key=lambda k: k['balance'] + k['bankbalance'], reverse=True)
        places = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th']
        entries = []

        count = 0
        for item in data:
            try:
                user = self.bot.get_user(int(item["_id"]))
                if user is None:
                    count -= 1
                else:
                    entries.append([places[count], user, "${:,}".format(int(item["balance"] + item["bankbalance"]))])
            except (KeyError, IndexError):
                entries.append([places[count], "Invalid User", 0])
            count += 1
            if count == 10:
                break

        output = ("```" + tabulate(entries, tablefmt="simple", headers=["#", "Player", "Balance"]) + "```")
        embed = discord.Embed(title="<:coin:733930163817152565> Highest Total Balances:", description=output, color=discord.Color.gold())
        await ctx.send(embed=embed)

    @baltop.error
    async def baltop_error(self, ctx, error):
        self.bot.errors += 1
        self.bot.important_errors += 1
        embed = discord.Embed(title=":x: Leaderboard Error", description="There was an error fetching infortmation. If you wish, you may [report this](https://discord.gg/zAZ3vKJ).")
        await ctx.send(embed=embed)


    @commands.command()
    async def frogtop(self, ctx):
        data = await self.bot.inventories.get_all()

        all = {}
        for item in data:
            for i in item["inventory"]:
                if i["name"] == "Frog":
                    all[item["_id"]] = i["quantity"]

        all = sorted(all.items(), key=lambda k: k[1], reverse=True)
        places = ['1st', '2nd', '3rd', '4th', '5th']
        entries = []

        count = 0
        for i in all:
            try:
                user = self.bot.get_user(int(all[count][0]))
                if user is None:
                    count -= 1
                else:
                    entries.append([places[count], user, all[count][1]])
            except (KeyError, IndexError):
                entries.append([places[count], "Invalid User", 0])
            count += 1
            if count == 5:
                break

        output = ("```" + tabulate(entries, tablefmt="simple", headers=["#", "Player", "Amount"]) + "```")
        embed = discord.Embed(title=":frog: Most Frogs:", description=output, color=discord.Color.gold())
        await ctx.send(embed=embed)

    @frogtop.error
    async def frogtop_error(self, ctx, error):
        self.bot.errors += 1
        self.bot.important_errors += 1
        embed = discord.Emebd(title=":x: Leaderboard Error", description="There was an error fetching infortmation. If you wish, you may [report this](https://discord.gg/zAZ3vKJ).")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Leaderboards(bot))
