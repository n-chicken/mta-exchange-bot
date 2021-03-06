# coding=utf-8

from sqlalchemy import Column, String, Date, DateTime, Integer, Numeric, ForeignKey, Sequence, Boolean, BigInteger
from datetime import datetime
from sql_base import Base
from sqlalchemy.sql import func


class Shop(Base):
    __tablename__ = 'shop'

    owner_id = Column(BigInteger, primary_key=True)
    channel_id = Column(BigInteger)

    def __init__(self, owner_id, channel_id):
        self.owner_id = owner_id
        self.channel_id = channel_id


class UserReview(Base):
    __tablename__ = 'user_review'

    reviewer_id = Column(BigInteger, primary_key=True)
    reviewed_id = Column(BigInteger, primary_key=True)
    rating = Column(Integer)
    comment = Column(String(280))

    def __init__(self, reviewer, reviewed, rating, comment):
        self.reviewer_id = reviewer.id
        self.reviewed_id = reviewed.id
        self.rating = rating
        self.comment = comment


class Ad(Base):
    __tablename__ = 'ad'

    id = Column(Integer, autoincrement=True, primary_key=True)
    intention = Column(String(4))
    offer = Column(String(280))
    returns = Column(String(280))
    negotiable = Column(Boolean, default=True)
    author_id = Column(BigInteger)
    author_name = Column(String(64))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    def __init__(self, intention, offer, returns, negotiable, user):
        self.intention = intention
        self.offer = offer
        self.returns = returns
        self.negotiable = negotiable
        self.author_id = user.id
        self.author_name = user


class Bid(Base):
    __tablename__ = 'bid'

    id = Column(Integer, autoincrement=True, primary_key=True)
    ad_id = Column(Integer, ForeignKey('ad.id'))
    bid_author_id = Column(BigInteger)
    bid_author_name = Column(String(64))
    bid_content = Column(String(280))

    def __init__(self, ad_id, bid_content, author_id, author_name):
        self.ad_id = ad_id
        self.bid_content = bid_content
        self.author_id = author_id
        self.author_name = author_name
