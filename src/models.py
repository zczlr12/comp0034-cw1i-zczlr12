from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from src import db


class Account(db.Model):
    user_id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.Text, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.Text, unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(db.Text, nullable=False)
    last_name: Mapped[str] = mapped_column(db.Text, nullable=False)
    email: Mapped[str] = mapped_column(db.Text, unique=True, nullable=False)
