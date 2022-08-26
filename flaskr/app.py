from . import create_app
from flask import jsonify
from .models import Ebook

app = create_app()

@app.route('/')
def hello_world():
    return 'Hello, Docker!'

@app.route('/ebook', methods=["GET"])
def getEbook():
    return jsonify(Ebook.query.all())

@app.route('/ebook', methods=["POST"])
def postEbook():
    return Ebook.query.all()
