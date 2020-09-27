import asyncio, utils.functions
from asyncinit import asyncinit
from overrides import overrides

@asyncinit
class InventoryArray(list):
    async def __new__(cls, user):
        if user is not None:
            inventory = await utils.functions.getInventory(user)
            if inventory is not None:
                return super(InventoryArray, cls).__new__(cls)

    async def __init__(self, user):
        inventory = await utils.functions.getInventory(user)
        super(InventoryArray, self).__init__(inventory)
        self.user = user

    async def contains(self, item):
        if self is None: return False
        for i in self:
            if i["name"].lower().replace(" ", "") == item["name"].lower():
                return True
        return False

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

        await bot.inventories.upsert({"_id": self.user.id, "inventory": self})

    @overrides
    async def remove(self, item):
        c = 0
        done = False
        for i in self:
            if i["name"] == item["name"]:
                if i["quantity"] == 1:
                    self.pop(c)
                else:
                    i["quantity"] -= 1
                change = True
            c += 1
        if not change:
            return False
        await bot.inventories.upsert({"_id": self.user.id, "inventory": self})
