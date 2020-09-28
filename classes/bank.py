import asyncio, utils.functions
from asyncinit import asyncinit

@asyncinit
class Bank:
    async def __new__(cls, user):
        if user is not None:
            if await utils.functions.getData(user) is not None:
                return super(Bank, cls).__new__(cls)

    async def __init__(self, user):
        data = await utils.functions.getData(user)
        self.balance = data["bankbalance"]
        self.limit = data["banklimit"]
