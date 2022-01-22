# <img src="https://static.wikia.nocookie.net/minecraft_gamepedia/images/3/33/Netherite_Scrap_JE2_BE1.png" alt="MarineGEO circle logo" style="height: 48px; width:48px;"/> MTA Exchange v2 Bot

## What this could be:
A way for anyone to show interest in buying or selling items on MTA. 
Disclaimer: We're not responsible for users that act in bad-faith, so trade wisely.

## Premises
- Each auction, trade and offer (added via /auction, /buying, /selling or /offer commands) has a integer ID, and each can be refered to as a "signal".

## Commands

- `/auction create <item ID | item name> [amount] [time]` - create an auction, possibly with a time limit

- `/auction list [item ID | item name]` - lists auctions optionally filtering by item name or ID

- `/search <item ID | item name>` - should be able to list all signals containing item name or ID

- `/info <user>` - lists all registered information about a user, including their signals

- `/buying <item ID | item name> [amount]` - signal that you're looking to buy something

- `/selling <item ID | item name> [amount]` - signal that you're looking to sell something

- `/remove <auction ID | trade ID | offer ID>` - removes a previously added signal

- `/offer <user> <auction ID | trade ID> <offer: string>` - makes a formal bid to a signal

- `/source` - sends source file as a direct message

## Roles

- Unverified
- Trusted (has at least one transaction confirmed by other verified member and has shown his IGN in MTA)
- Very-Trusted (has at least 5 transactions confirmed by distinct verified members)

## To-do/Issues:

- Create better help command & clarify command structure
- Should "shops" be a thing?
- Add autocomplete in contexts where item ids are possible arguments
  - Maybe include popular kits?
- Add timed auctions?
- Add trust-ranking system?
- Users are notified when they receive an offer
- Should users be penalized if they don't have the item they are registered to sell?
  - Alternatively, automatically remove old user data within a yet-to-be-determined time frame

## Setup / Contributing
Follow this [tutorial on how to setup a discord bot](https://www.youtube.com/watch?v=ygc-HdZHO5A) to get a discord token key with the appropriate permissions. After you get the key, just run the script as: 

```
python bot.py <your key> [-g <your channel's ID>]
```

Or alternatively add it as an environment variable and run the script with no arguments.
