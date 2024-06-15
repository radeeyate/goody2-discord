# goody2-bot

I while ago (a few months ago), I found [goody2](https://good2.ai). It seemed cool, so I thought to myself, "I should make a Discord bot that lets you use it."
That's exactly what I did. The Discord bot uses discord.py to connect to Discord and aiohttp to connect to goody2's API.

Goody2 can store conversations, so you must set up a MongoDB database to store the info. You can get one for free from MongoDB Atlas.
The environment variable example is stored in [.env.example](./.env.example). Please modify the values in it to make it work properly.
You will also need a Discord bot token.

Once you have the environment variable file that has been renamed to `.env`, you can proceed to starting the bot:

```shell
# On Linux or MacOS (probably)
python3 bot.py

# On Windows
python bot.py
```

If everything goes well, the bot should be started. In any channel that the bot is in, you can type `g2! whateveryourmessageishere` to send a message to goody2.
Goody2 limits conversations to 4-6 messages from my testing. If you reach your limit, you can reset the conversation by typing `g2!reset`.