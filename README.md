# <img src="https://static.wikia.nocookie.net/minecraft_gamepedia/images/3/33/Netherite_Scrap_JE2_BE1.png" alt="logo" style="height: 32px; width: 32px;"/> MTA Exchange v2 Bot

## What this could be:
A way for anyone to show interest in buying or selling items on MTA. 
Disclaimer: We're not responsible for users that act in bad-faith, so trade wisely.

## Commands

- `/search <user | query>` - search for ads

- `/bid <ad ID> <your_bid>` - makes a formal bid to an ad

- `/buy <offer> <returns> [negotiable]` - signal that you're looking to buy something

- `/sell <offer> <returns> [negotiable]` - signal that you're looking to sell something

- `/remove <ad ID>` - removes a previously added ad

- `/reviews <user>` - list user reviews

- `/review <user> <rate> [comment]` - reviews a user's shop

- `/source` - sends source file as a direct message

- `/create_shop` - creates a shop

## To-do/Issues:

- [x] Create better help command & clarify command structure
- [x] Should "shops" be a thing?
- [ ] ~~Add autocomplete in contexts where item ids and names are possible arguments~~
  - ~~Maybe include popular kits?~~
- ~~Add trust-ranking system?~~
- [ ] Users are to be directly notified when they receive an /bid
- [ ] Limit ad count per player unless they're "very" trusted
- [ ] Automatically remove old user data within a yet-to-be-determined time frame
- [ ] Better search
- [ ] Handle disconnects

## Setup / Contributing

### Version
Python 3.8+

### Database

To run the database, just use `docker-compose up`. To reset it, run `docker-compose down` and the former command.

### Key

Follow this [tutorial on how to setup a discord bot](https://www.youtube.com/watch?v=ygc-HdZHO5A) to get a discord token key with the appropriate permissions. 

After you have setup the database and got the key, set it as environment variable named `MTA_EXCHANGE_DISCORD_BOT_TOKEN`, then run the main script:

```
python main.py
```

Or just run the script like this:

```
python main.py <your_token>
```

Notice you have to overwrite the guild ID with your channel for it to work outside MTA Exchange Discord Server (`-g` flag). 
