#!/usr/bin/env python
from signals import Signal
from disnake import User
from sql_base import *
from signals import *

sess = session_factory()

class SignalService:

    def add_auction(self, item_sold: str, item_recv: str, intention: str, item_sold_amount: int, item_recv_amount: int, user: User, limit=None):
        auction = Auction(item_sold, item_recv, intention, item_sold_amount, item_recv_amount, user, limit)
        sess.add(auction)
        sess.commit()

    def list_auctions(self, user: User=None):
        pass

    def rm_auction(self, user: User):
        pass
