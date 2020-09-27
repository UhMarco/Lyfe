import asyncio, discord
from asyncinit import asyncinit
from classes.inventory import InventoryArray

@asyncinit
class User(discord.user.User): # Extends discord.User so all discord.py attributes is the same
    async def __init__(self, user):
        self.inventory = await InventoryArray(user)

    async def hasItem(self, item):
        if self.inventory is None: return False

        for i in self.inventory:
            if i["name"].lower().replace(" ", "") == item["name"].lower():
                return True
        return False

    async def giveItem(self, item):
        found = False
        for i in self.inventory:
            if i["name"] == item["name"]:
                i["quantity"] += 1
                found = True

        if not found:
            del item["emoji"], item["value"], item["description"], item["rarity"]
            item["locked"] = False
            item["quantity"] = 1
            self.inventory.append(item)

        await bot.inventories.upsert({"_id": self.discord.id, "inventory": self.inventory})
