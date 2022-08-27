from . import create_app, bcrypt, db
from .models import Ebook, Staff

from http import HTTPStatus
from flask import Response, request
from flask_login import login_user, current_user, login_required, logout_user


app = create_app()

@app.route('/')
def hello_world():
    return 'Hello, Docker!'

@app.route('/ebook', methods=["GET"])
def getEbook():
    return Response(
        Ebook.query.all(),
        status=200,
        )

@app.route('/ebook', methods=["POST"])
def postEbook():
    return Ebook.query.all()


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

@app.route("/admin/logout", methods=["POST"])
@login_required
def adminLogout():
    logout_user()
    return Response('user logged out', status=HTTPStatus.OK)

@app.route("/admin/whoami", methods=["GET"])
@login_required
def adminWhoami():
    return Response(str(current_user), status=HTTPStatus.OK)
