#!/usr/bin/env python
from disnake import User
from sql_base import *
from entities import *

sess = session_factory()

class TradeService:

    def add_ad(self, intention, offer, returns, negotiable, user: User):
        ad = Ad(intention, offer, returns, negotiable, user)
        sess.add(ad)
        sess.commit()
        return ad

    def list_ads(self, user: User=None):
        q = sess.query(Ad)
        if user is not None:
            q = q.filter_by(author=user.id)
        return list(q)
