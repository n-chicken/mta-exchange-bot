#!/usr/bin/env python
from datetime import datetime
from discord.ext import commands
from disnake import User, Colour, Embed
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
    for item in items:
        try:
            index = string.index(item)
            item_len[item] = len(item)
        except:
            continue
    if not item_len:
        return 'kit' if 'kit' in string else None
    return max(item_len, key=item_len.get)


# https://leovoel.github.io/embed-visualizer/
def embed_ad(ad: Ad, author: User, deleted: bool = False) -> Embed:
    is_buy = ad.intention == 'buy'
    title = ''
    if deleted:
        title += 'Deleted '
    title += f'Ad #{ad.id}'
    description = 'Looking to ' + ('buy ' if is_buy else 'sell ') + ad.offer
    target_item = find_item(ad.offer)
    other_item = find_item(ad.returns)
    if is_buy:
        description += ' and offers ' + ad.returns
    else:
        description += ' and expects ' + ad.returns
    if deleted:
        color = Colour.red()
    else:
        color = Colour.orange() if is_buy else Colour.green()
    embed = Embed(
        title=title,
        description=description,
        colour=color
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
AD_NOT_FOUND = 'Ad not found'
UNAUTHORIZED = 'Unauthorized'
AD_OFFER_EQ_RETURNS = 'Offer may not be the same as expected returns'
TBI = 'To be implemented'

# -------------------------------------------------------------


class Confirm(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @disnake.ui.button(label="Confirm", style=disnake.ButtonStyle.green)
    async def confirm(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message("Confirming", ephemeral=True)
        self.value = True
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @disnake.ui.button(label="Cancel", style=disnake.ButtonStyle.grey)
    async def cancel(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message("Cancelling", ephemeral=True)
        self.value = False
        self.stop()


class Menu(disnake.ui.View):
    def __init__(self, embeds: list[disnake.Embed]):
        super().__init__(timeout=None)

        # Sets the embed list variable.
        self.embeds = embeds

        # Current embed number.
        self.embed_count = 0

        # Disables previous page button by default.
        self.prev_page.disabled = True

        # Sets the footer of the embeds with their respective page numbers.
        for i, embed in enumerate(self.embeds):
            embed.set_footer(text=f"Page {i + 1} of {len(self.embeds)}")

    @disnake.ui.button(label="Previous page", emoji="◀️", style=disnake.ButtonStyle.red)
    async def prev_page(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        # Decrements the embed count.
        self.embed_count -= 1

        # Gets the embed object.
        embed = self.embeds[self.embed_count]

        # Enables the next page button and disables the previous page button if we're on the first embed.
        self.next_page.disabled = False
        if self.embed_count == 0:
            self.prev_page.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="Quit", emoji="❌", style=disnake.ButtonStyle.red)
    async def remove(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.edit_message(view=None)

    @disnake.ui.button(label="Next page", emoji="▶️", style=disnake.ButtonStyle.green)
    async def next_page(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        # Increments the embed count.
        self.embed_count += 1

        # Gets the embed object.
        embed = self.embeds[self.embed_count]

        # Enables the previous page button and disables the next page button if we're on the last embed.
        self.prev_page.disabled = False
        if self.embed_count == len(self.embeds) - 1:
            self.next_page.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

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
async def search(ctx, query: str = None, user: User = None, ad_id: int = None):
    if not (query or user or ad_id):
        await ctx.send(INVALID_SEARCH)
        return
    ads = trade_service.search(search_query=query, user=user, ad_id=ad_id)
    if not ads:
        emoji = rand_emoji()
        await ctx.send('No results ' + emoji)
    embeds = []
    for ad in ads:
        ad_author = await bot.fetch_user(ad.author_id)
        embeds += [embed_ad(ad, ad_author)]

    embeds[0].set_footer(text=f"Page 1 of {len(embeds)}")
    await ctx.send(embed=embeds[0], view=Menu(embeds))


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
async def bid(ctx, ad_id: int, bid_content: str):
    bid = trade_service.bid(ad_id, bid_content, ctx.author)
    ad = trade_service.find_ad(bid.ad_id)
    ad_author = await bot.fetch_user(ad.author_id)
    bidder = ctx.author
    await ctx.send(embed=embed_bid(bid, bidder, ad_author))


@bot.slash_command()
async def source(ctx):
    await ctx.send('https://github.com/n-chicken/mta-exchange-bot')


@bot.slash_command()
async def help(ctx):
    help = """
Commands:
/sell
/buy
/bid
/remove
/source
    """
    await ctx.send(help)

# -------------------------------------------------------------

if __name__ == '__main__':
    bot.run(args.token)
