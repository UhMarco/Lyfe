import asyncio, utils.functions
from asyncinit import asyncinit

@asyncinit
class Inventory(list):
    async def __new__(cls, user):
        if user is not None:
            if await utils.functions.getData(user) is not None:
                return super(Inventory, cls).__new__(cls)

    async def __init__(self, user):
        inventory = await utils.functions.getInventory(user)
        super(Inventory, self).__init__(inventory)
        self.user = user

    def contains(self, item):
        if self is None: return False
        for i in self:
            if i["name"].lower().replace(" ", "") == item["name"].lower().replace(" ", ""):
                return True
        return False

    def get(self, item):
        if self is None: return None
        for i in self:
            if i["name"].lower().replace(" ", "") == item["name"].lower().replace(" ", ""):
                return i
        return None

    def add(self, item):
        added_item = dict(item)
        found = False
        for i in self:
            if i["name"] == added_item["name"]:
                i["quantity"] += 1
                found = True

        if not found:
            del added_item["emoji"], added_item["value"], added_item["description"], added_item["rarity"]
            added_item["locked"] = False
            added_item["quantity"] = 1
            self.append(added_item)

    def remove(self, item):
        c = 0
        for i in self:
            if i["name"] == item["name"]:
                if i["quantity"] == 1:
                    self.pop(c)
                else:
                    i["quantity"] -= 1
            c += 1
