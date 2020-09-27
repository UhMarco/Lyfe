from classes.user import User

async def getUser(user):
    user = bot.get_user(int(user.strip("<!@>")))
    if user is not None:
        user = await User(user)
    return user

async def getInventory(user):
    data = await bot.inventories.find(user.id)
    if data is not None:
        data = data["inventory"]
    return data

async def getAllItems():
    items = await bot.items.find("items")
    return items["items"]

async def getItem(item):
    items = await getAllItems()
    item.lower().replace(" ", "")
    if item not in items:
        return None
    return items[item]
