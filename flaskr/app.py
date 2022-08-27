from . import create_app, bcrypt, db
from .models import Ebook, Staff
from .schema import EbookSchema

from http import HTTPStatus
from flask import Response, request, jsonify
from flask_login import login_user, current_user, login_required, logout_user


app = create_app()

@app.route('/')
def hello_world():
    return 'Hello, Docker!'

# Public
@app.route('/ebook', methods=["GET"])
def getAllEbook():
    return jsonify(EbookSchema(many=True).dump(Ebook.query.all()))

@app.route("/ebook/<int:id>", methods=["GET"])
def getEbookWithID(id):
    return EbookSchema().dump(Ebook.query.filter_by(id=id).first())

# Admin User Auth
@app.route("/admin/register", methods=["POST"])
def adminRegister():
    try:
        hashed_password = bcrypt.generate_password_hash(request.args.get('password')).decode('utf-8')
        staff = Staff(
            name=request.args.get('name'),
            email=request.args.get('email'),
            phone_number=request.args.get('phone_number'),
            address=request.args.get('address'),
            password=hashed_password
        )
        db.session.add(staff)
        db.session.commit()
    except Exception as err:
        return Response(f'{err}', status=HTTPStatus.BAD_REQUEST)

    return Response("Registration success", status=HTTPStatus.OK)


@app.route("/admin/login", methods=["POST"])
def adminLogin():
    staff: Staff = Staff.query.filter_by(email=request.args.get('email')).first()
    if staff and bcrypt.check_password_hash(staff.password, request.args.get('password')):
        login_user(user=staff)
        return Response("success", status=HTTPStatus.OK)
    return Response('validation error, check email or password', status=HTTPStatus.BAD_REQUEST)


# Admin Ebooks
@app.route("/admin/ebook", methods=["POST"])
def postEbookasAdmin():
    ebook = Ebook(
        judul=request.args.get('judul'),
        penulis=request.args.get('penulis'),
        sinopsis=request.args.get('sinopsis'),
        harga=int(request.args.get('harga')),
        image_url=request.args.get('image_url'),
        content_url=request.args.get('content_url'),
    )
    db.session.add(ebook)
    db.session.commit()

    return EbookSchema().dump(ebook)



@app.route("/admin/ebook/<int:id>", methods=["GET"])
@login_required #TODO: Granular role access control
def getEbookWithIDasAdmin(id):
    return getEbookWithID(id)

@app.route("/admin/ebook", methods=["GET"])
@login_required #TODO: Granular role access control
def getAllEbookasAdmin():
    return getAllEbook()

@app.route("/admin/ebook/<int:id>", methods=["PUT"])
@login_required #TODO: Granular role access control
def putEbookWithIDasAdmin(id):
    ebook = Ebook.query.filter_by(id=id).first()
    ebook.judul=request.args.get('judul')
    ebook.penulis=request.args.get('penulis')
    ebook.sinopsis=request.args.get('sinopsis')
    ebook.harga=int(request.args.get('harga'))
    ebook.image_url=request.args.get('image_url')
    ebook.content_url=request.args.get('content_url')

    db.session.commit()

    return EbookSchema().dump(ebook)

@app.route("/admin/ebook/<int:id>", methods=["DELETE"])
@login_required #TODO: Granular role access control
def deleteEbookWithIDasAdmin(id):
    ebook = Ebook.query.filter_by(id=id).first()
    if ebook:
        db.session.delete(ebook)
        db.session.commit()
        return Response(status=HTTPStatus.OK)

    return Response(status=HTTPStatus.NOT_FOUND)

# Extras
@app.route("/admin/logout", methods=["GET"])
@login_required #TODO: Granular role access control
def adminLogout():
    logout_user()
    return Response('user logged out', status=HTTPStatus.OK)

@app.route("/admin/whoami", methods=["GET"])
@login_required #TODO: Granular role access control
def adminWhoami():
    return Response(str(current_user), status=HTTPStatus.OK)
