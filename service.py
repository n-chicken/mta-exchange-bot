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

    def search(self, search_query, user, ad_id):
        q = sess.query(Ad)
        if search_query is not None:
            lhs_clause = Ad.offer.like(f'%{search_query}%')
            rhs_clause = Ad.returns.like(f'%{search_query}%')
            q = q.filter(or_(lhs_clause, rhs_clause))
        if user is not None:
            q = q.filter_by(author_id=user.id)
        if ad_id is not None:
            q = q.filter_by(id=ad_id)
        return q.all()

    def find_ad(self, id) -> Ad:
        return sess.query(Ad).filter_by(id=id).first()

    def remove_ad(self, id, requesting_user):
        ad = self.find_ad(id)
        print(ad.deleted_at)
        if not ad or ad.deleted_at:
            raise AdNotFoundException()
        if ad.author_id == requesting_user.id:
            ad.deleted_at = datetime.now()
            sess.add(ad)
            sess.commit()
            return ad
        else:
            raise UnauthorizedException()

    def bid(self, ad_id, bid_content, user):
        ad = self.find_ad(ad_id)
        if not ad:
            raise AdNotFoundException()
        bid = Bid(ad.id, bid_content, user.id, user.name)
        sess.add(bid)
        sess.commit()
        return bid

        
