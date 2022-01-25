#!/usr/bin/env python
from datetime import datetime
from discord.ext import commands
from disnake import User
from disnake.ext import commands
from entities import *
from exceptions import *
from service import TradeService
import argparse
import asyncio
import discord
import disnake
import json
import os
import random
import re
import sys

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


def find_item(string):
    item_index = {}
    for item in items:
        try:
            index = string.index(item)
            item_index[item] = len(item)
        except:
            continue
    if not item_index:
        return 'kit' if 'kit' in string else None
    return max(item_index, key=item_index.get)


# https://leovoel.github.io/embed-visualizer/
def embed_ad(ad: Ad, author: User) -> disnake.Embed:
    is_buy = ad.intention == 'buy'
    title = f'Ad #{ad.id}'
    description = 'Looking to ' + ('buy ' if is_buy else 'sell ') + ad.offer
    target_item = find_item(ad.offer)
    other_item = find_item(ad.returns)
    if is_buy:
        description += ' and offers ' + ad.returns
    else:
        description += ' and expects ' + ad.returns
    embed = disnake.Embed(
        title=title,
        description=description,
        colour=disnake.Colour.orange() if is_buy else disnake.Colour.green()
    )
    if not is_buy:
        aux = target_item
        target_item = other_item
        other_item = aux
    if target_item and target_item not in ['air', 'kit']:
        file_target_item = disnake.File(
            f'data/item-icons/{target_item}.png', filename="target.png")
        embed.set_thumbnail(file=file_target_item)
    if other_item and other_item not in ['air', 'kit']:
        file_other_item = disnake.File(
            f'data/item-icons/{other_item}.png', filename="other.png")
        embed.set_image(file=file_other_item)
    if author:
        embed.set_author(name=author.name, icon_url=author.display_avatar.url)

    if not ad.negotiable:
        embed.set_footer(text=f'🔒 Non-Negotiable')
    return embed


def embed_bid(bid: Bid, bidder: User, author: User) -> disnake.Embed:
    ad = trade_service.find_ad(bid.ad_id)
    is_ad_buy = ad.intention == 'buy'
    if not ad:
        raise AdNotFoundException()
    description = bidder.name + ' just bid:\n\n' + bid.bid_content
    embed = disnake.Embed(
        title=f'Ad #{ad.id}',
        description=description,
        colour=disnake.Colour.blue() if is_ad_buy else disnake.Colour.yellow()
    )
    bid_content_item = find_item(bid.bid_content)
    if bid_content_item and bid_content_item != 'kit':
        file_bid_content_item = disnake.File(
            f'data/item-icons/{bid_content_item}.png', filename="bid_content_item.png")
        embed.set_thumbnail(file=file_bid_content_item)

    ad_content_item = find_item(ad.offer)
    if ad_content_item and ad_content_item != 'kit':
        file_other_item = disnake.File(
            f'data/item-icons/{ad_content_item}.png', filename="other.png")
        embed.set_image(file=file_other_item)
    embed.set_footer(text='for ' + author.name + '\'s ' + ad.offer)
    embed.set_author(name=bidder.name, icon_url=bidder.display_avatar.url)
    return embed


# -------------------------------------------------------------


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

# -------------------------------------------------------------

INVALID_PROPOSAL_ERROR = ' must be at most 280 characters long'
INVALID_SEARCH = 'Search for either a user or an item or both'
AD_OFFER_EQ_RETURNS = 'Offer may not be the same as expected returns'
TBI = 'To be implemented'

# -------------------------------------------------------------


async def signal_trade(ctx, intention, offer, returns, negotiable):
    if len(offer) > 280:
        await ctx.send('Offer' + INVALID_PROPOSAL_ERROR)
        return
    if len(returns) > 280:
        await ctx.send('Returns' + INVALID_PROPOSAL_ERROR)
        return
    ad = trade_service.add_ad(
        intention, offer, returns, negotiable, ctx.author)
    await ctx.send(embed=embed_ad(ad, ctx.author))


@bot.slash_command()
async def sell(ctx, offer: str, returns: str, negotiable: bool = True):
    await signal_trade(ctx, 'sell', offer, returns, negotiable)


@bot.slash_command()
async def buy(ctx, offer: str, returns: str, negotiable: bool = True):
    await signal_trade(ctx, 'buy', offer, returns, negotiable)


@bot.slash_command()
async def search(ctx, query: str = None, user: User = None):
    if not query and not user:
        await ctx.send(INVALID_SEARCH)
        return
    ads = trade_service.search(search_query=query, user=user)
    if not ads:
        rand = random.randint(0, 1) % 3
        if rand == 0:
            emoji = '<:youdidwhat:934477030525919242>'
        elif rand == 1:
            emoji = '<:what:934477030618177566>'
        else:
            emoji = '<:pepenosign:934477030270066740>'
        await ctx.send('No results ' + emoji)
    for ad in ads:
        author = await bot.fetch_user(ad.author_id)
        await ctx.send(embed=embed_ad(ad, author))


@bot.slash_command()
async def info(ctx):
    await ctx.send(TBI)


@bot.slash_command()
async def remove(ctx, ad_id: int):
    await ctx.send(TBI)


@bot.slash_command()
async def bid(ctx, ad_id: int, bid_content: str):
    bid = trade_service.bid(ad_id, bid_content, ctx.author)
    ad = trade_service.find_ad(bid.ad_id)
    ad_author = await bot.fetch_user(ad.author_id)
    bidder = ctx.author
    await ctx.send(embed=embed_bid(bid, bidder, ad_author))


@bot.slash_command()
async def source(ctx):
    await ctx.send(TBI)


@bot.slash_command()
async def help(ctx):
    help = """
Commands:
/sell
/buy
/bid
/remove - To be implemented
/info - To be implemented
    """
    await ctx.send(help)

# -------------------------------------------------------------

if __name__ == '__main__':
    bot.run(args.token)
