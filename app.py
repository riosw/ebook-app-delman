from crypt import methods
from . import create_app
from .models import db, Ebook

app = create_app()

@app.route('/')
def hello_world():
    return 'Hello, Docker!'

@app.route('/ebook', methods=["GET"])
def getEbook():
    return Ebook.query.all()
