from . import db, login_manager

from flask_login import UserMixin

class Ebook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.Text())

    def __repr__(self) -> str:
        return f'Ebook<id={self.id},judul={self.judul}>'

# tells the login manager on how to get the user
@login_manager.user_loader
def load_user(user_id):
    return Staff.query.get(int(user_id))

class Staff(db.Model, UserMixin):
    name = db.Column(db.Text(), nullable=False)
    email = db.Column(db.Text(), unique=True, nullable=False)
    phone_number = db.Column(db.Text(), nullable=False)
    address = db.Column(db.Text(), nullable=False)
    password = db.Column(db.Text(), nullable=False)

    def __repr__(self) -> str:
        return f'{self.name}, {self.email}'
