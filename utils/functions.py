from classes.user import User

async def confirm(ctx):
    message = ctx.message
    await ctx.send("Please confirm.")
    def check(m):
        return m.channel == ctx.channel and m.author == ctx.author
    message = await bot.wait_for('message', check=check)
    if message.content.lower() == "confirm" or message.content.lower() == "yes":
        return True
    else:
        await ctx.send("Aborted.")
        return False


async def getUser(user):
    try:
        user = bot.get_user(int(user.strip("<!@>")))
    except Exception:
        user = None
    if user is not None:
        user = await User(user)
    return user

async def getData(user):
    return await bot.inventories.find(user.id)

async def getInventory(user):
    data = await bot.inventories.find(user.id)
    if data is not None:
        data = data["inventory"]
    return data

async def getBalance(user):
    data = await bot.inventories.find(user.id)
    if data is not None:
        data = data["balance"]
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

def prepareItem(item):
    try:
        del item["emoji"], item["value"], item["description"], item["rarity"]
    except KeyError:
        return None
    item["locked"] = False
    item["quantity"] = 1
    return item
