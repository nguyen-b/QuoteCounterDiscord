from datetime import datetime
import os
import re

from discord.ext import tasks, commands
import pytz

from quote_bot import QuoteBot


CH_ID = int(os.getenv('CH_ID'))
PATTERN = re.compile(r'(?:\*\*(.*)\*\*)+')
TZ = pytz.timezone(os.getenv('TZ'))

bot = commands.Bot(command_prefix='$')
bot.remove_command("help")
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


@bot.event
async def on_ready():
    await bot.wait_until_ready()

    channel = bot.get_channel(CH_ID)
    monthly.start(channel)


@bot.event
async def on_message(message):
    if message.channel.id == CH_ID and message.author.id != bot.user.id:
        dt = message.created_at
        res = re.findall(PATTERN, message.content)
        if res:
            for name in res:
                qb.add_quote(name.lower(), dt.month, dt.year)
        await bot.process_commands(message)


@bot.command(name='add')
async def _add(ctx, name):
    dt = ctx.message.created_at
    qb.add_quote(name.lower(), dt.month, dt.year)
    await ctx.message.add_reaction(EMOJI)


@bot.command(name='counts')
async def _counts(ctx, month, year):
    if month.isnumeric() and year.isnumeric():
        counts = qb.counts(month, year)
        await command_response(ctx, counts)


@bot.command(name='dump')
async def _dump(ctx):
    await command_response(ctx, qb.dump())


@bot.command(name='help')
async def _help(ctx):
    await command_response(ctx, qb.help_text())


@bot.command(name='remove')
async def _remove(ctx, name):
    dt = ctx.message.created_at
    qb.remove_quote(name.lower(), dt.month, dt.year)
    await ctx.message.add_reaction(EMOJI)


@bot.command(name='tally')
async def _tally(ctx, month, year):
    if month.isnumeric() and year.isnumeric():
        tally = qb.monthly_tally(month, year)
        await command_response(ctx, tally)


async def command_response(ctx, message):
    res = qb.random_greeting() + "\n\n"
    res += message
    await ctx.channel.send(res)


bot.run(os.getenv('TOKEN'))
