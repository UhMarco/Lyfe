import asyncio
from asyncinit import asyncinit
from utils.functions import getInventory

@asyncinit
class InventoryArray(list):
    async def __init__(self, user):
        inventory = await getInventory(user)
        super(InventoryArray, self).__init__(inventory)
        self.discord = user

    async def add(self, item):
        found = False
        for i in self:
            if i["name"] == item["name"]:
                i["quantity"] += 1
                found = True

        if not found:
            del item["emoji"], item["value"], item["description"], item["rarity"]
            item["locked"] = False
            item["quantity"] = 1
            self.append(item)

        await bot.inventories.upsert({"_id": self.discord.id, "inventory": self})
