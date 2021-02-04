import discord
import os
import pytz
import re

from datetime import datetime
from discord.ext import tasks
from quote_bot import QuoteBot


CH_ID = int(os.getenv('CH_ID'))
PATTERN = re.compile(r'(?:\*\*(.*)\*\*)+')
TZ = pytz.timezone(os.getenv('TZ'))

client = discord.Client()
qb = QuoteBot(os.getenv("DB"), os.getenv('GREET'))

EMOJI = "\U0001F6AB"

@tasks.loop(hours=1)
async def monthly(channel):
        date = datetime.now(TZ)
        if date.day == 1 and date.hour == 0:
            last_month = date.month - 1
            curr_year = date.year
            res = qb.monthly_tally(last_month, curr_year)
            await channel.send(res)


@client.event
async def on_ready():
    await client.wait_until_ready()

    channel = client.get_channel(CH_ID)
    monthly.start(channel)

@client.event
async def on_message(message):
    if message.channel.id == CH_ID and message.author.id != client.user.id:
        dt = message.created_at
        if message.content.startswith('$help'):
            await message.channel.send(qb.help_text())
        elif message.content.startswith('$counts'):
            params = qb.parse_params(message.content)
            if params:
                counts = qb.counts(params[1], params[2])
                await message.channel.send(counts)
        elif message.content.startswith('$tally'):
            params = qb.parse_params(message.content)
            if params:
                tally = qb.monthly_tally(params[1], params[2])
                await message.channel.send(tally)
        elif message.content.startswith('$dump'):
            await message.channel.send(qb.dump())
        elif message.content.startswith('$add'):
            params = qb.parse_params(message.content)
            if params:
                name = params[1]
                qb.add_quote(name.lower(), dt.month, dt.year)
                await message.add_reaction(EMOJI)
        elif message.content.startswith('$remove'):
            params = qb.parse_params(message.content)
            if params:
                name = params[1]
                qb.remove_quote(name.lower(), dt.month, dt.year)
                await message.add_reaction(EMOJI)
        else:
            res = re.findall(PATTERN, message.content)
            if res:
                for name in res:
                    qb.add_quote(name.lower(), dt.month, dt.year)

client.run(os.getenv('TOKEN'))
