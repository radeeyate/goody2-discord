import discord
import aiohttp
from dotenv import load_dotenv
import os
import pymongo

load_dotenv()
BOT_TOKEN = os.getenv("TOKEN")
db = pymongo.MongoClient(os.getenv("CONNECTION_STRING"))["goody2"]
users = db["users"]


class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_message(self, message):
        print(f"Message from {message.author}: {message.content}")
        if message.author == self.user:
            return

        if message.content.startswith("g2!"):
            if message.content == "g2!reset":
                users.update_one({"userid": message.author.id}, {"$set": {"token": ""}})
                await message.reply("Reset chat.")
                return

            await message.channel.trigger_typing()
            sentence = await processMessage(message.author.id, message)
            await message.reply(sentence, mention_author=True)


async def processMessage(userID, message):
    sentence = ""
    convoToken = await getConversationToken(userID)
    async with aiohttp.request(
        "post",
        "https://goody2.ai/send",
        json={
            "message": message.content.replace("g2!", "").strip(),
            "conversationToken": convoToken,
        },
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Connection": "keep-alive",
        },
    ) as resp:
        async for line, _ in resp.content.iter_chunks():
            if not line:
                continue

            line = line.decode("utf-8")
            print(line)
            if "max_turns" in line:
                await updateConversationToken(userID, "")
                return "Max messages reached. Send g2!reset to reset."
            if 'conversation":"' in line:
                for line in line.splitlines():
                    if not 'data: {"conversation":"' in line:
                        sentence += await sanatizeMessage(line)
                    else:
                        token = line.replace('data: {"conversation":"', "").replace(
                            '"}', ""
                        )
                        #print("token is:", token)
            else:
                sentence += await sanatizeMessage(line)
    if not users.find_one({"userid": userID}):
        await addUser(userID, token)
    await updateConversationToken(userID, token)
    return sentence


async def addUser(userID, token):
    users.insert_one({"userid": userID, "token": token})


async def updateConversationToken(userID, token):
    users.update_one({"userid": userID}, {"$set": {"token": token}})


async def getConversationToken(userID):
    userData = users.find_one({"userid": userID})
    return userData["token"] if userData else ""


async def sanatizeMessage(message):
    return (
        message.replace("event: message", "")
        .replace("data: ", "")
        .replace('"', '"')
        .replace('"}', "")
        .replace('{"content":"', "")
        .replace("\n", "")
    )


intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(BOT_TOKEN)
