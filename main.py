import logging
from logging.handlers import RotatingFileHandler
import os

import discord


class DiscordBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print('hi')

    async def on_message(self, message: discord.Message):
        if not message.author.bot:
            logging.getLogger('discord_bot_raspi').log(logging.INFO, message.content)
            await message.channel.send(message.content)


if __name__ == '__main__':
    handler = RotatingFileHandler(
        filename='logs/discord_bot_raspi.log',
        encoding='utf-8',
        maxBytes=32,
        backupCount=5,
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)

    logger = logging.getLogger('discord_bot_raspi')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

    import django
    django.setup()

    bot = DiscordBot(intents=discord.Intents.all())

    bot.run(os.getenv('DISCORD_BOT_KEY', 'error'))
