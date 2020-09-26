async def hasItem(user, item):
    data = await bot.inventories.find(user.id)
    if data is None: return False
    inventory = data["inventory"]
    for i in inventory:
        if i["name"].lower().replace(" ", "") == item.lower():
            return True
    return False

async def getUser(ctx, user):
    if len(ctx.message.mentions) == 0:
        try:
            user = bot.get_user(int(user))
            if user is None:
                await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
                return None
        except ValueError:
            await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
            return None
    else:
        user = ctx.message.mentions[0]
    return user

async def getAllItems():
    items = await bot.items.find("items")
    return items["items"]

async def getItem(item):
    items = await getAllItems()
    item.lower().replace(" ", "")
    if item not in items:
        return None
    return items[item]
