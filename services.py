#!/usr/bin/env python
from disnake import User
from entities import *
from exceptions import *
from sql_base import *
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
import code

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
            lhs_clause = Ad.offer.ilike(f'%{search_query}%')
            rhs_clause = Ad.returns.ilike(f'%{search_query}%')
            q = q.filter(or_(lhs_clause, rhs_clause))
        if user is not None:
            q = q.filter_by(author_id=user.id)
        if ad_id is not None:
            q = q.filter_by(id=ad_id)
        q = q.filter_by(deleted_at=None)
        return q.all()

    def find_ad(self, id) -> Ad:
        return sess.query(Ad).filter_by(id=id).first()

    def remove_ad(self, id, requesting_user):
        ad = self.find_ad(id)
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


class UserService:

    def review(self, reviewer, reviewed, rate, comment):
        persisted_review = self._find_review(reviewer.id, reviewed.id)
        if persisted_review:
            user_review = UserReview(reviewer, reviewed, 0, 0)
            user_review.rating = rate
            user_review.comment = comment
        else:
            user_review = UserReview(reviewer, reviewed, rate, comment)
        sess.merge(user_review)
        sess.commit()
        return user_review

    def _find_review(self, reviewer_id, reviewed_id):
        q = sess.query(UserReview)
        q = q.filter_by(reviewer_id=reviewer_id)
        q = q.filter_by(reviewed_id=reviewed_id)
        return q.one_or_none(),

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

    def get_reviews(self, user):
        q = sess.query(UserReview.reviewer_id,
                       UserReview.rating, UserReview.comment)
        q = q.filter_by(reviewed_id=user.id)
        return q.all()
