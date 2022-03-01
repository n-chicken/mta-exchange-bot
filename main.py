#!/usr/bin/env python
# code.interact(banner='', local=globals().update(locals()) or globals(), exitmsg='')
from datetime import datetime
from disnake import User, Colour, Embed, File
from disnake.ext import commands
from disnake.ext.commands import has_permissions
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
from tendo.singleton import SingleInstance
# -------------------------------------------------------------

SingleInstance()

ADMIN_ID = 776924572896460830
SHOP_CATEGORY_ID = 935334812603002950
TEST_GUILD_ID = 815757801133441115
BOT_CENTER_CHANNEL_ID = 934266756871102495
ENV_TOKEN = os.environ.get('MTA_EXCHANGE_DISCORD_BOT_TOKEN')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MTA Exchange v2 Bot')
    parser.add_argument('token', nargs='?', default=ENV_TOKEN)
    parser.add_argument('-g', '--guild', type=int, default=TEST_GUILD_ID)
    parser.add_argument('-S', '--dont-sync-commands', action='store_true')
    args = parser.parse_args()
    if not args.token:
        print('Missing Discord token!', file=sys.stderr)
        sys.exit(1)
else:
    sys.exit(1)

bot = commands.Bot(
    # command_prefix='$',
    test_guilds=[args.guild],
    sync_commands=not args.dont_sync_commands
)

items = json.load(open('data/minecraft-items.json'))

trade_service = TradeService()
user_service = UserService()
shop_service = ShopService()

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
        description=f'Current rating: {mean_rating:.2f}\n{"⭐"*int(mean_rating)}\n{"-"*20}',
        colour=Colour.purple()
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    for reviewer, review in peoples_comments.items():
        rating, comment = review
        if not comment:
            comment = '-'
        embed.add_field(
            name=f'{reviewer} rated\n' + '⭐'*rating, value=comment, inline=False)
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


async def dictfy_reviews(reviews):
    peoples_comments = {}
    for reviewer_id, rating, comment in reviews:
        reviewer = await bot.fetch_user(reviewer_id)
        peoples_comments[reviewer] = (rating, comment)
    return peoples_comments

# -------------------------------------------------------------


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}, ID: {bot.user.id}")


@bot.event
async def on_message(message):
    if message.channel.id == BOT_CENTER_CHANNEL_ID:
        await message.delete()


@bot.event
async def on_raw_reaction_add(reaction):
    requester_id = reaction.user_id
    if requester_id != bot.user.id:
        owner_id, = shop_service.get_owner_id(reaction.channel_id)
        guild = bot.get_guild(reaction.guild_id)
        shop_owner = await guild.fetch_member(owner_id)
        dm_channel = await shop_owner.create_dm()
        await dm_channel.send(f'<@{requester_id}> intends to make a purchase off your shop')


# -------------------------------------------------------------

PROPOSAL_TOO_LONG = ' must be at most 280 characters long'
INVALID_SEARCH = 'Search for either a user or an item or both'
AD_NOT_FOUND = 'Ad not found'
UNAUTHORIZED = 'Unauthorized'
ALREADY_SHOP_OWNER = 'Already owns a shop'
TBI = 'To be implemented'
AD_OFFER_EQ_RETURNS = 'Offer may not be the same as expected returns'
INVALID_RATING = 'Rating must be between 0 and 5'
ALREADY_REVIEWED = 'You already reviewed this user'
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
    # ↓ Send an error message to the user if the ad is not found
    try:
        bid = trade_service.bid(ad_id, bid_content, ctx.author)
    except AdNotFoundException:
        await ctx.send(f"**{AD_NOT_FOUND}!** (id: {str(ad_id)})")
    ad = trade_service.find_ad(bid.ad_id)
    ad_author = await bot.fetch_user(ad.author_id)
    await ad_author.send(f"**@{ctx.author}** bid **{bid_content}** on you ad for **{ad.offer}**. (ID: **{str(ad_id)}**)")
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
    mean_rating = user_service.get_mean_rating(user)
    peoples_comments = await dictfy_reviews(user_service.get_reviews(user))
    await ctx.send(embed=embed_user_info(user, mean_rating, peoples_comments, from_=ctx.author))


@bot.slash_command()
async def reviews(ctx, user: User):
    mean_rating = user_service.get_mean_rating(user)
    peoples_comments = await dictfy_reviews(user_service.get_reviews(user))
    await ctx.send(embed=embed_user_info(user, mean_rating, peoples_comments))


@bot.slash_command()
async def remove_ad(ctx, ad_id: int):
    try:
        ad = trade_service.remove_ad(ad_id, ctx.author)
        ad_author = await bot.fetch_user(ad.author_id)
        await ctx.send(embed=embed_ad(ad, ad_author, deleted=True))
    except AdNotFoundException:
        await ctx.send(AD_NOT_FOUND)
    except UnauthorizedException:
        await ctx.send(UNAUTHORIZED)


@bot.slash_command()
async def create_shop(ctx, use_react_message=True, react_message='React to this message to request the shop owner', react_message_emoji='💰'):
    user = ctx.author
    try:
        exists = shop_service.exists(user)
        if exists:
            await ctx.send(ALREADY_SHOP_OWNER)
            return
    except Exception as e:
        print(e)
        await ctx.send(ALREADY_SHOP_OWNER)
        return
    shops_category = disnake.utils.get(
        ctx.guild.categories, id=SHOP_CATEGORY_ID)
    new_channel = await ctx.guild.create_text_channel(ctx.author.display_name, category=shops_category)
    shop_service.register(ctx.author, new_channel.id)
    message = await new_channel.send(react_message)
    await message.add_reaction(react_message_emoji)
    shop_owner_role = disnake.utils.get(ctx.guild.roles, name="Shop Owner")
    everyone_role = ctx.guild.default_role
    owner = await ctx.guild.fetch_member(user.id)
    owner_perms = ctx.channel.overwrites_for(owner)
    everyone_perms = ctx.channel.overwrites_for(everyone_role)
    everyone_perms.send_messages = False
    everyone_perms.read_messages = True
    everyone_perms.view_channel = True
    everyone_perms.read_message_history = True
    owner_perms.manage_channels = True
    owner_perms.manage_messages = True
    owner_perms.read_messages = True
    owner_perms.view_channel = True
    owner_perms.send_messages = True
    owner_perms.read_message_history = True
    await new_channel.set_permissions(owner, overwrite=owner_perms)
    await new_channel.set_permissions(everyone_role, overwrite=everyone_perms)
    await owner.add_roles(shop_owner_role)


@bot.slash_command()
async def source(ctx):
    await ctx.send('https://github.com/n-chicken/mta-exchange-bot')


@bot.slash_command()
async def help(ctx):
    help = """Commands:
/bid
/buy
/create_shop
/remove_ad
/review
/reviews
/sell
/source
    """
    await ctx.send(help)


@has_permissions(administrator=True)
@bot.slash_command()
async def clear_bot_center_chat(ctx):
    channel = ctx.guild.get_channel(BOT_CENTER_CHANNEL_ID)
    messages = await channel.history(limit=1000).flatten()
    for message in messages:
        if message.author.id != bot.user.id:
            message.delete()

@has_permissions(administrator=True)
@bot.slash_command()
async def migrate_legacy_shops(ctx, channel_id, react_message: str = 'React to this message to request the shop owner.', emoji: str = '💰'):
    # legacy channels 👇
    # 'chad': 935534377994174515,
    # 'feather': 935344402631622706,
    # 'secretpasser': 935357068444049439,
    # 'szin': 935348447291244635,
    # 'vort': 937867613277659216,
    channel = ctx.guild.get_channel(user_channel_ids[channel_id])
    message = await channel.send(react_message)
    await message.add_reaction(emoji)


# -------------------------------------------------------------

if __name__ == '__main__':
    bot.run(args.token)
