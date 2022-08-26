from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Ebook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.Text())
    # penulis
    # sinopsis
    # harga
    # image_url
    # content_url