# coding=utf-8

from sqlalchemy import Column, String, Date, DateTime, Integer, Numeric, ForeignKey, Sequence

from sql_base import Base


class Signal(Base):
    __tablename__ = 'signal'

    id = Column(Integer, autoincrement=True, primary_key=True)
    item_sold = Column(String(64), primary_key=True)
    item_recv = Column(String(64), primary_key=True)
    author = Column(String(64), primary_key=True)
    intention = Column(String(4), primary_key=True)
    item_sold_amount = Column(Integer)
    item_recv_amount = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity':'signal'
    }

    def __init__(self, item_sold, item_recv, author, intention, item_sold_amount, item_recv_amount):
        self.item_sold = item_sold
        self.item_recv = item_recv 
        self.author = author 
        self.intention = intention 
        self.item_sold_amount = item_sold_amount
        self.item_recv_amount = item_recv_amount

class Auction(Signal):
    __tablename__ = 'auction'

    id = Column(Integer, ForeignKey('signal.id'), primary_key=True)
    auction_id = Column(Integer, autoincrement=True, primary_key=True)
    limit = Column(DateTime())

    __mapper_args__ = {
        'polymorphic_identity':'auction',
    }

    def __init__(self, item_sold, item_recv, author, intention, item_sold_amount, item_recv_amount, limit=None):
        super(self.__class__, self).__init__(item_sold, item_recv, author, intention, item_sold_amount, item_recv_amount)
        self.limit = limit

class Bid(Signal):
    __tablename__ = 'bid'

    signal_id  = Column(Integer, ForeignKey('signal.id'), primary_key=True)
    auction_id  = Column(Integer, ForeignKey('auction.auction_id'), primary_key=True)
    bid_id = Column(Integer, autoincrement=True, primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'bid',
    }
