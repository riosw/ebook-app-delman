from email.policy import default
from . import db, login_manager

from flask_login import UserMixin
from sqlalchemy_utils import EmailType, PhoneNumberType, ChoiceType
from enum import Enum
from datetime import datetime

class Ebook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.Text())
    penulis = db.Column(db.Text())
    sinopsis = db.Column(db.Text())
    harga = db.Column(db.Integer)
    image_url = db.Column(db.Text())
    content_url = db.Column(db.Text())

    def __repr__(self) -> str:
        return f'Ebook<id={self.id},judul={self.judul}>'

# Tells the login manager on how to get the user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class UserTypes(Enum):
    staff=1
    customer=2


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    email = db.Column(EmailType, unique=True, nullable=False)
    phone_number = db.Column(PhoneNumberType, nullable=False)
    address = db.Column(db.Text(), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(ChoiceType(UserTypes, impl=db.Integer()), nullable=False)

    def __repr__(self) -> str:
        return f'{self.name}, {self.email}, {self.role.value}'


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer = db.relationship("User", backref="orders")
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    ebook = db.relationship("Ebook", backref="orders")
    ebook_id = db.Column(db.Integer, db.ForeignKey("ebook.id"))
    harga = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
