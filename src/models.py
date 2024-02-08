from typing import List
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src import db


class Account(db.Model):
    __tablename__ = "account"
    user_id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.Text, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.Text, unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(db.Text, nullable=False)
    last_name: Mapped[str] = mapped_column(db.Text, nullable=False)
    email: Mapped[str] = mapped_column(db.Text, unique=True, nullable=False)
    comments: Mapped[List["Comment"]] = relationship(back_populates="account")


class Comment(db.Model):
    __tablename__ = "comment"
    comment_id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    date: Mapped[str] = mapped_column(db.Text, nullable=False)
    content: Mapped[str] = mapped_column(db.Text, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("account.user_id"))
    account: Mapped["Account"] = relationship("Account", back_populates="comments")


class Item(db.Model):
    __tablename__ = "item"
    item_id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.Text, nullable=False)
    brand_number: Mapped[int] = mapped_column(db.Integer, nullable=False)
    item_number: Mapped[int] = mapped_column(db.Integer, nullable=False)
    data: Mapped[List["Data"]] = relationship(back_populates="item")


class Data(db.Model):
    __tablename__ = "data"
    data_id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    date: Mapped[datetime] = mapped_column(db.DateTime, nullable=False)
    quantity: Mapped[int] = mapped_column(db.Integer, nullable=False)
    promotion: Mapped[bool] = mapped_column(db.Boolean, nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("item.item_id"))
    item: Mapped["Item"] = relationship("Item", back_populates="data")
