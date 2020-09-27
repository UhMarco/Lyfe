import asyncio, discord
from asyncinit import asyncinit
from classes.inventory import InventoryArray

@asyncinit
class User(discord.user.User): # Extends discord.User so all discord.py attributes is the same
    async def __init__(self, user):
        self.inventory = await InventoryArray(user)
