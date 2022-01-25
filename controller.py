#!/usr/bin/env python
# code.interact(banner='', local=globals().update(locals()) or globals(), exitmsg='')
from datetime import datetime
from discord.ext import commands
from disnake import User, Colour, Embed, File
from disnake.ext import commands
from entities import *
from exceptions import *
from services import *
import argparse
import asyncio
import code
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
user_service = UserService()

# -------------------------------------------------------------


def rand_emoji():
    rand = random.randint(0, 1) % 3
    if rand == 0:
        emoji = '<:youdidwhat:934477030525919242>'
    elif rand == 1:
        emoji = '<:what:934477030618177566>'
    else:
        emoji = '<:pepenosign:934477030270066740>'
    return emoji


def find_item(string):
    item_len = {}
    lower_string = string.lower()
    for item in items:
        try:
            index = lower_string.index(item)
            item_len[item] = len(item)
        except:
            continue
    if not item_len:
        return 'kit' if 'kit' in lower_string else None
    return max(item_len, key=item_len.get)


# https://leovoel.github.io/embed-visualizer/
def embed_ad(ad: Ad, author: User, deleted: bool = False, created: bool = False) -> Embed:
    is_buy = ad.intention == 'buy'
    title = ''
    if deleted:
        title += 'Deleted '
    if created:
        title += 'Posted '
    title += f'Ad #{ad.id}'
    target_item = find_item(ad.offer)
    other_item = find_item(ad.returns)
    if deleted:
        color = Colour.red()
    elif is_buy:
        color = Colour.orange()
    else:
        color = Colour.green()
    embed = Embed(
        title=title,
        colour=color
    )
    if not is_buy:
        aux = target_item
        target_item = other_item
        other_item = aux

    if target_item and target_item not in ['air', 'kit']:
        file_target_item = File(
            f'data/item-icons/{target_item}.png', filename="target.png")
        embed.set_thumbnail(file=file_target_item)
    if other_item and other_item not in ['air', 'kit']:
        file_other_item = File(
            f'data/item-icons/{other_item}.png', filename="other.png")
        embed.set_image(file=file_other_item)
    if author:
        embed.set_author(name=author.display_name,
                         icon_url=author.display_avatar.url)
    verb = 'Is looking to buy:' if is_buy else 'Is looking to sell:'
    embed.add_field(name=f'{verb}', value=ad.offer, inline=False)
    embed.add_field(name='For:', value=ad.returns, inline=False)
    if not ad.negotiable:
        embed.set_footer(text=f'🔒 Non-Negotiable')
    return embed


def embed_user_info(user: User, mean_rating: float, peoples_comments: dict, from_: User = None) -> Embed:
    if from_:
        title = from_.display_name + ' rated ' + user.display_name
    else:
        title = user.display_name
    embed = Embed(
        title=title,
        description=f'Current rating: {mean_rating:.2f} - {"⭐"*int(mean_rating)}\n {"-"*20}',
        colour=Colour.purple()
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    for reviewer, review in peoples_comments.items():
        rating, comment = review
        if not comment:
            comment = '-'
        embed.add_field(
            name=f'{reviewer} rated ' + '⭐'*rating, value=comment, inline=False)
    return embed


def embed_bid(bid: Bid, bidder: User, author: User) -> Embed:
    ad = trade_service.find_ad(bid.ad_id)
    is_ad_buy = ad.intention == 'buy'
    if not ad:
        raise AdNotFoundException()
    embed = Embed(
        title=f'Just bid on Ad #{ad.id}:',
        description=bid.bid_content,
        colour=Colour.blue() if is_ad_buy else Colour.yellow()
    )
    bid_content_item = find_item(bid.bid_content)
    if bid_content_item and bid_content_item != 'kit':
        file_bid_content_item = File(
            f'data/item-icons/{bid_content_item}.png', filename="bid_content_item.png")
        embed.set_thumbnail(file=file_bid_content_item)

    ad_content_item = find_item(ad.offer)
    if ad_content_item and ad_content_item != 'kit':
        file_other_item = File(
            f'data/item-icons/{ad_content_item}.png', filename="other.png")
        embed.set_image(file=file_other_item)
    noun = 'request' if is_ad_buy else 'offer'
    embed.add_field(
        name=f'For {author.display_name}\'s {noun}:', value=ad.offer, inline=False)
    embed.set_author(name=bidder.display_name,
                     icon_url=bidder.display_avatar.url)
    return embed


# -------------------------------------------------------------


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}, ID: {bot.user.id}")

# -------------------------------------------------------------

PROPOSAL_TOO_LONG = ' must be at most 280 characters long'
INVALID_SEARCH = 'Search for either a user or an item or both'
AD_NOT_FOUND = 'Ad not found'
UNAUTHORIZED = 'Unauthorized'
AD_OFFER_EQ_RETURNS = 'Offer may not be the same as expected returns'
INVALID_RATING = 'Rating must be between 1 and 5'
ALREADY_REVIEWED = 'You already reviwed this user'
CANT_RATE_URSLEF = 'Can\'t rate yourself, smartass'

# -------------------------------------------------------------


async def signal_trade(ctx, intention, offer, returns, negotiable):
    if len(offer) > 280:
        await ctx.send('Offer' + PROPOSAL_TOO_LONG)
        return
    if len(returns) > 280:
        await ctx.send('Returns' + PROPOSAL_TOO_LONG)
        return
    ad = trade_service.add_ad(
        intention, offer, returns, negotiable, ctx.author)
    await ctx.send(embed=embed_ad(ad, ctx.author, created=True))


@bot.slash_command()
async def sell(ctx, offer: str, returns: str, negotiable: bool = True):
    await signal_trade(ctx, 'sell', offer, returns, negotiable)


@bot.slash_command()
async def buy(ctx, thing_wanted: str, returns: str, negotiable: bool = True):
    await signal_trade(ctx, 'buy', thing_wanted, returns, negotiable)


@bot.slash_command()
async def bid(ctx, ad_id: int, bid_content: str):
    if len(bid_content) > 280:
        await ctx.send(PROPOSAL_TOO_LONG)
        return
    bid = trade_service.bid(ad_id, bid_content, ctx.author)
    ad = trade_service.find_ad(bid.ad_id)
    ad_author = await bot.fetch_user(ad.author_id)
    await ctx.send(embed=embed_bid(bid, ctx.author, ad_author))


@bot.slash_command()
async def search(ctx, query: str = None, user: User = None, ad_id: int = None):
    if not (query or user or ad_id):
        await ctx.send(INVALID_SEARCH)
        return
    ads = trade_service.search(search_query=query, user=user, ad_id=ad_id)
    if not ads:
        await ctx.send('No results ' + rand_emoji())
        return
    for ad in ads:
        ad_author = await bot.fetch_user(ad.author_id)
        await ctx.send(embed=embed_ad(ad, ad_author))


async def dictfy_reviews(reviews):
    peoples_comments = {}
    for reviewer_id, rating, comment in reviews:
        reviewer = await bot.fetch_user(reviewer_id)
        peoples_comments[reviewer] = (rating, comment)
    return peoples_comments


@bot.slash_command()
async def review(ctx, user: User, rating: int, comment: str = None):
    if user.id == ctx.author.id:
        await ctx.send(CANT_RATE_URSLEF)
        return
    if not (0 <= rating <= 5):
        await ctx.send(INVALID_RATING)
        return
    try:
        review = user_service.review(ctx.author, user, rating, comment)
    except AlreadyReviewedException:
        await ctx.send(ALREADY_REVIEWED)
        return
    # await ctx.send(embed=embed_review(review))
    mean_rating = user_service.get_mean_rating(user)
    peoples_comments = await dictfy_reviews(user_service.get_reviews(user))
    await ctx.send(embed=embed_user_info(user, mean_rating, peoples_comments, from_=ctx.author))


@bot.slash_command()
async def reviews(ctx, user: User):
    mean_rating = user_service.get_mean_rating(user)
    peoples_comments = await dictfy_reviews(user_service.get_reviews(user))
    await ctx.send(embed=embed_user_info(user, mean_rating, peoples_comments))


@bot.slash_command()
async def remove(ctx, ad_id: int):
    try:
        ad = trade_service.remove_ad(ad_id, ctx.author)
        ad_author = await bot.fetch_user(ad.author_id)
        await ctx.send(embed=embed_ad(ad, ad_author, deleted=True))
    except AdNotFoundException:
        await ctx.send(AD_NOT_FOUND)
    except UnauthorizedException:
        await ctx.send(UNAUTHORIZED)


@bot.slash_command()
async def source(ctx):
    await ctx.send('https://github.com/n-chicken/mta-exchange-bot')


@bot.slash_command()
async def help(ctx):
    help = """Commands:
/sell
/buy
/bid
/remove
/source
/review
/reviews
    """
    await ctx.send(help)

# -------------------------------------------------------------

if __name__ == '__main__':
    bot.run(args.token)
