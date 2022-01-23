#!/usr/bin/env python
import discord
from discord.ext import commands
import asyncio
# from discord_slash import SlashCommand, SlashContext
# from discord_slash.utils.manage_commands import create_choice, create_option
import disnake
from disnake import User
from disnake.ext import commands
from datetime import datetime
import os
import re
import argparse
import sys
import json
from signals import *
from service import SignalService

# -------------------------------------------------------------

SOURCE_PATH = os.path.realpath(__file__)

BOT_TOKEN_KEY = 'MTA_EXCHANGE_DISCORD_BOT_TOKEN'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MTA Exchange v2 Bot')
    parser.add_argument('token', nargs='?', default=os.environ.get(BOT_TOKEN_KEY))
    parser.add_argument('-g', '--guild', type=int, default=815757801133441115)
    args = parser.parse_args()
else:
    sys.exit(1)

bot = commands.Bot(command_prefix="$", test_guilds=[args.guild])

items = json.load(open('data/minecraft-items.json'))

signal_service = SignalService()

# -------------------------------------------------------------

# Events
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

# -------------------------------------------------------------

# Commands
@bot.slash_command()
async def auction(ctx):
    await asyncio.sleep(0)

@auction.sub_command()
async def create(ctx, item_sold: str, item_recv: str, intention: str, item_sold_amount: int, item_recv_amount: int, limit=None):
    if intention not in ['buy', 'sell']:
        await ctx.send('Intention must be either to `buy` or `sell`')
    signal_service.add_auction(item_sold, item_recv, ctx.author, intention, item_sold_amount, item_recv_amount, limit)
    await ctx.send('Auction created')

@auction.sub_command()
async def list(ctx, user: User=None):
    auctions = signal_service.list_auctions(user)
    await ctx.send('Auctions: ' + str(auctions))

@bot.slash_command()
async def info(ctx):
    await ctx.send('To be implemented')

@bot.slash_command()
async def buying(ctx):
    await ctx.send('To be implemented')

@bot.slash_command()
async def selling(ctx):
    await ctx.send('To be implemented')

@bot.slash_command()
async def remove(ctx):
    await ctx.send('To be implemented')

@bot.slash_command()
async def bid(ctx, user: disnake.User):
    await ctx.send('To be implemented')

@bot.slash_command()
async def source(ctx):
    await ctx.send('To be implemented')

# -------------------------------------------------------------

if __name__ == '__main__':
    bot.run(args.token)
