import asyncio, discord
from asyncinit import asyncinit
from classes.inventory import InventoryArray

@asyncinit
class User:
    async def __init__(self, user):
        # Extending discord.User stopped working for no reason so you'll need
        # to access it by using the following:
        self.discord = user
        self.inventory = await InventoryArray(user)
