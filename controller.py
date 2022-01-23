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
from entities import *
from service import TradeService

# -------------------------------------------------------------

SOURCE_PATH = os.path.realpath(__file__)

BOT_TOKEN_KEY = 'MTA_EXCHANGE_DISCORD_BOT_TOKEN'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MTA Exchange v2 Bot')
    parser.add_argument('token', nargs='?',
                        default=os.environ.get(BOT_TOKEN_KEY))
    parser.add_argument('-g', '--guild', type=int, default=815757801133441115)
    args = parser.parse_args()
else:
    sys.exit(1)

bot = commands.Bot(test_guilds=[args.guild])

items = json.load(open('data/minecraft-items.json'))

trade_service = TradeService()

# -------------------------------------------------------------


def find_item_in_offer(offer):
    item_index = {}
    for item in items:
        try:
            index = offer.index(item)
            item_index[item] = index
        except:
            continue
    if not item_index:
        return 'kit'
    return min(item_index, key=item_index.get)


def create_embed(ad: Ad, author: User) -> disnake.Embed:
    is_buy = ad.intention == 'buy'
    title = f'Ad #{ad.id}'
    description = 'Is ' + ('looking to buy ' if is_buy else 'selling ') + ad.offer
    target_item = find_item_in_offer(ad.offer)
    other_item = find_item_in_offer(ad.returns)
    if is_buy:
        description += ' and expects ' + ad.returns
    else:
        description += ' and offers ' + ad.returns
    embed = disnake.Embed(
        title=title,
        description=description,
        colour=disnake.Colour.orange() if is_buy else disnake.Colour.green()
    )
    if target_item and target_item != 'kit':
        file_target_item = disnake.File(
            f'data/item-icons/{target_item}.png', filename="target.png")
        embed.set_thumbnail(file=file_target_item)
    if other_item and other_item != 'kit':
        file_other_item = disnake.File(
            f'data/item-icons/{other_item}.png', filename="other.png")
        embed.set_image(file=file_other_item)
    if author:
        embed.set_author(name=author.name, icon_url=author.display_avatar.url)
    # embed.add_field(name="FN1", value="FV1", inline=True)
    # embed.add_field(name="FN2", value="FV2", inline=True)

    if ad.negotiable:
        embed.set_footer(text=f'This ad is negotiable')
    else:
        embed.set_footer(text=f'Non-Negotiable')
    return embed

# -------------------------------------------------------------


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

# -------------------------------------------------------------

INVALID_ITEM_ERROR = 'Target item must be a valid minecraft string id or a kit'
INVALID_PROPOSAL_ERROR = ' must be at most 280 characters long'
INVALID_SEARCH = 'Search for either a user or an item or both'
INVALID_TARGET_ITEM = 'Target item must be a valid minecraft string id or a kit'
TBI = 'To be implemented'

# -------------------------------------------------------------

async def signal_trade(ctx, intention, offer, returns, negotiable):
    if len(offer) > 280:
        await ctx.send('Offer' + INVALID_PROPOSAL_ERROR)
        return
    if len(returns) > 280:
        await ctx.send('Returns' + INVALID_PROPOSAL_ERROR)
        return
    if offer not in items and 'kit' not in offer.lower():
        await ctx.send(INVALID_ITEM_ERROR)
        return
    ad = trade_service.add_ad(intention, offer, returns, negotiable, ctx.author)
    await ctx.send(embed=create_embed(ad, ctx.author))


@bot.slash_command()
async def sell(ctx, offer: str, returns: str, negotiable: bool=True):
    await signal_trade(ctx, 'sell', offer, returns, negotiable)


@bot.slash_command()
async def buy(ctx, offer: str, returns: str, negotiable: bool=True):
    await signal_trade(ctx, 'buy', offer, returns, negotiable)

@bot.slash_command()
async def search(ctx, item: str=None, user: User=None):
    if not item and not user:
        await ctx.send(INVALID_SEARCH)
        return
    if item not in items:
        await ctx.send(INVALID_TARGET_ITEM)
        return
    ads = trade_service.search(item=item, user=user)
    for ad in ads:
        await ctx.send(embed=create_embed(ad, ad.author))


@bot.slash_command()
async def info(ctx):
    await ctx.send(TBI)


@bot.slash_command()
async def remove(ctx):
    await ctx.send(TBI)


@bot.slash_command()
async def bid(ctx, user: disnake.User):
    await ctx.send(TBI)


@bot.slash_command()
async def source(ctx):
    await ctx.send(TBI)

# -------------------------------------------------------------

if __name__ == '__main__':
    bot.run(args.token)
