#!/usr/bin/env python
import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
import datetime
import os
import re
import argparse
import sys
from sql_base import session_factory
from signals import Signal

BOT_TOKEN_KEY = 'MTA_EXCHANGE_DISCORD_BOT_TOKEN'
bot = commands.Bot(command_prefix='/')
slash = SlashCommand(bot, sync_commands=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MTA Exchange v2 Bot')
    parser.add_argument('token', nargs='?', default=os.environ.get(BOT_TOKEN_KEY))
    parser.add_argument('-g', '--guild', type=int, default=815757801133441115)
    args = parser.parse_args()
else:
    sys.exit(1)

async def require_subcommand(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("Command can't be invoked without a subcommand")

# option_types for @slash.slash
# 1: SUB_COMMAND
# 2: SUB_COMMAND_GROUP
# 3: STRING
# 4: INTEGER
# 5: BOOLEAN
# 6: USER
# 7: CHANNEL
# 8: ROLE

@slash.slash(
        name='ping',
        description='pings the bot',
        guild_ids=[args.guild],
        options=[
            create_option(
                name="option",
                description="choose word",
                required=True,
                option_type=1
                )
            ]
        )
@bot.command()
async def ping(ctx, option: str):
    await ctx.send('pong')

@slash.slash(
        name='Auction',
        description='Lists and creates auctions',
        guild_ids=[args.guild],
        options=[
            ]
        )
async def auction(ctx):
    await require_subcommand(ctx)

@bot.command(name='list')
async def _list(ctx, *args):
    ctx.send('test!')

# -------------------------------------------

def get_signals():
    session = session_factory()
    signal_query = session.query(Signal)
    session.close()
    return signal_query.all()

# @slash.slash(
#         name='info',
#         description='provides bot info',
#         guild_ids=[guild_id]
#         )
# async def info(ctx):
#     embed = discord.Embed(title=f"{ctx.guild.name}", description="", timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
#     embed.add_field(name="Server created at", value=f"{ctx.guild.created_at}")
#     embed.add_field(name="Server Owner", value=f"{ctx.guild.owner}")
#     embed.add_field(name="Server Region", value=f"{ctx.guild.region}")
#     embed.add_field(name="Server ID", value=f"{ctx.guild.id}")
#     # embed.set_thumbnail(url=f"{ctx.guild.icon}")
#     embed.set_thumbnail(url="https://pluralsight.imgix.net/paths/python-7be70baaac.png")
#
#     await ctx.send(embed=embed)

# Events
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="commands"))
    print('Bot start')

@bot.listen()
async def on_message(message):
    pass
    # if "tutorial" in message.content.lower():
    #     await message.channel.send('This is that you want http://youtube.com/fazttech')
    #     await bot.process_commands(message)

if __name__ == '__main__':
    bot.run(args.token)
