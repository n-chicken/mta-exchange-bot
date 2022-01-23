#!/usr/bin/env python
from disnake import User
from sql_base import *
from entities import *
from sqlalchemy import or_
from sqlalchemy import and_
from exceptions import *

sess = session_factory()

class TradeService:

    def add_ad(self, intention, offer, returns, negotiable, user):
        ad = Ad(intention, offer, returns, negotiable, user)
        sess.add(ad)
        sess.commit()
        return ad

    def search(self, search_query, user):
        q = sess.query(Ad)
        if search_query is not None:
            lhs_clause = and_(Ad.offer.like(f'%{search_query}%'), Ad.intention == 'sell')
            rhs_clause = and_(Ad.returns.like(f'%{search_query}%'), Ad.intention == 'buy')
            q = q.filter(or_(lhs_clause, rhs_clause))
        if user is not None:
            q = q.filter_by(author_id=user.id)
        return q.all()

    def find_ad(self, id):
        return sess.query(Ad).filter_by(id=id).first()

    def bid(self, ad_id, bid_content):
        ad = self.find_ad(ad_id)
        if not ad:
            raise AdNotFoundException()
        bid = Bid(ad.id, bid_content)
        sess.add(bid)
        sess.commit()
        return bid

        
