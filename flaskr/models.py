from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Ebook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.Text())

    def __repr__(self) -> str:
        return f'Ebook<id={self.id},judul={self.judul}>'