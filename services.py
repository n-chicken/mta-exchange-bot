#!/usr/bin/env python
from disnake import User
from entities import *
from exceptions import *
from sql_base import *
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy import or_
import code
from time import sleep
import sys

SESSION_TIMEOUT_SECONDS = 3

sess = session()

# -------------------------------------------------------------


def recover_session():
    global sess
    if sess:
        try:
            sess.close()
        except:
            sess.rollback()
            sess.close()
    sess = None
    while not sess:
        try:
            sess = session()
        except:
            sleep(SESSION_TIMEOUT_SECONDS)


def sql_error_handler(f):
    def wrapper(*args, **kw):
        try:
            return f(*args, **kw)
        except OperationalError as e:
            print(e, file=sys.stderr)
            recover_session()
    return wrapper

# -------------------------------------------------------------


class TradeService:

    @sql_error_handler
    def add_ad(self, intention, offer, returns, negotiable, user):
        ad = Ad(intention, offer, returns, negotiable, user)
        sess.add(ad)
        sess.commit()
        return ad

    @sql_error_handler
    def search(self, search_query, user, ad_id):
        q = sess.query(Ad)
        if search_query is not None:
            lhs_clause = Ad.offer.ilike(f'%{search_query}%')
            rhs_clause = Ad.returns.ilike(f'%{search_query}%')
            q = q.filter(or_(lhs_clause, rhs_clause))
        if user is not None:
            q = q.filter_by(author_id=user.id)
        if ad_id is not None:
            q = q.filter_by(id=ad_id)
        q = q.filter_by(deleted_at=None)
        return q.all()

    @sql_error_handler
    def find_ad(self, id) -> Ad:
        return sess.query(Ad).filter_by(id=id).first()

    @sql_error_handler
    def remove_ad(self, id, requesting_user):
        ad = self.find_ad(id)
        if not ad or ad.deleted_at:
            raise AdNotFoundException()
        if ad.author_id == requesting_user.id or requesting_user.id == 776924572896460830:
            ad.deleted_at = datetime.now()
            sess.add(ad)
            sess.commit()
            sess.expunge_all()
            return ad
        else:
            raise UnauthorizedException()

    @sql_error_handler
    def bid(self, ad_id, bid_content, user):
        ad = self.find_ad(ad_id)
        if not ad:
            raise AdNotFoundException()
        bid = Bid(ad.id, bid_content, user.id, user.name)
        sess.add(bid)
        sess.commit()
        return bid


class UserService:

    @sql_error_handler
    def review(self, reviewer, reviewed, rate, comment):
        persisted_review, = self._find_review(reviewer.id, reviewed.id)
        if persisted_review:
            user_review = UserReview(reviewer, reviewed, 0, 0)
            user_review.rating = rate
            user_review.comment = comment
        else:
            user_review = UserReview(reviewer, reviewed, rate, comment)
        sess.merge(user_review)
        sess.commit()
        return user_review

    @sql_error_handler
    def _find_review(self, reviewer_id, reviewed_id):
        q = sess.query(UserReview)
        q = q.filter_by(reviewer_id=reviewer_id)
        q = q.filter_by(reviewed_id=reviewed_id)
        return q.one_or_none()

    @sql_error_handler
    def get_mean_rating(self, user):
        q = sess.query(UserReview)
        q = q.filter_by(reviewed_id=user.id)
        count = q.count()
        if count == 0:
            return 0
        q = sess.query(func.sum(UserReview.rating))
        q = q.filter_by(reviewed_id=user.id)
        sum, = q.one()
        return sum/count

    @sql_error_handler
    def get_reviews(self, user):
        q = sess.query(UserReview.reviewer_id,
                       UserReview.rating, UserReview.comment)
        q = q.filter_by(reviewed_id=user.id)
        return q.all()


class ShopService:

    @sql_error_handler
    def exists(self, owner):
        return sess.query(Shop).filter_by(owner_id=owner.id).one_or_none()

    @sql_error_handler
    def get_owner_id(self, channel_id):
        return sess.query(Shop.owner_id).filter_by(channel_id=channel_id).one_or_none()

    @sql_error_handler
    def register(self, owner, channel_id):
        shop = Shop(owner.id, channel_id)
        sess.merge(shop)
        sess.commit()
        return shop
