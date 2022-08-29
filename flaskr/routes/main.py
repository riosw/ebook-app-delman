from .. import bcrypt, db, login_manager
from ..models import Ebook, User, UserTypes, Order
from ..schema import EbookSchema, UserSchema, OrderSchema

from http import HTTPStatus
from flask import Response, request, jsonify, Blueprint
from flask_login import login_user, current_user, login_required, logout_user
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from typing import Optional
from functools import wraps

main = Blueprint('main', __name__)

@main.route('/')
def hello_world():
    return 'Hello, World!'

# Public ebook
@main.route('/ebook', methods=["GET"])
def getAllEbook():
    return jsonify(EbookSchema(many=True).dump(Ebook.query.all()))

@main.route("/ebook/<int:id>", methods=["GET"])
def getEbookWithID(id):
    return EbookSchema().dump(Ebook.query.filter_by(id=id).first())

def role_required(role:UserTypes):
    """Wraps route handlers to authenticate user roles before running the handler.
    For authentication with any roles, use flask_login.login_required decorator instead.

    Args:
        role (UserTypes): enumerated class of user type / role
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
               return login_manager.unauthorized()
            if (current_user.role != role):
                return login_manager.unauthorized()      
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

def ensureNoAuth():
    """Wraps route handlers to ensure current user has not been authenticated

    """
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if current_user.is_authenticated:
               return Response("This action cannot be done when client is logged in.\
            Please logout first", status=HTTPStatus.CONFLICT)   
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

# User Auth
# Register
@ensureNoAuth()
def userRegister(userType: UserTypes) -> Response:
    """Helper handler to register user

    Args:
        userType (UserTypes): enumerated class of user type / role

    Returns:
        Response
    """
    try:
        userArgs = request.args.to_dict()
        userArgs['role'] = userType.value

        errors = UserSchema().validate(userArgs)
        if errors:
            return Response(f'{errors}', status=HTTPStatus.BAD_REQUEST)
        
        hashed_password = bcrypt.generate_password_hash(userArgs.get('password')).decode('utf-8')
        
        staff = User(
            name=userArgs.get('name'),
            email=userArgs.get('email'),
            phone_number=userArgs.get('phone_number'),
            address=userArgs.get('address'),
            password=hashed_password,
            role=userArgs.get('role')
        )

        db.session.add(staff)
        db.session.commit()
    except Exception as err:
        if isinstance(err, IntegrityError) and isinstance(err.orig, UniqueViolation):
            return Response(f'This email already exists', status=HTTPStatus.BAD_REQUEST)

        return Response(f'{err}', status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return Response("Registration success", status=HTTPStatus.OK)

@main.route("/admin/register", methods=["POST"])
def adminRegister():
    return userRegister(userType=UserTypes.staff)

@main.route("/customer/register", methods=["POST"])
def customerRegister():
    return userRegister(userType=UserTypes.customer)

#Login
@ensureNoAuth()
def userLogin(userType: UserTypes, returnUser: Optional[bool] = False) -> Response:
    """Helper handler to login user

    Args:
        userType (UserTypes): enumerated class of user type / role
        returnUser (Optional[bool], optional): If True, return user data as response
            else, return success message. Defaults to False.

    Returns:
        Response
    """    
    user: User = User.query.filter_by(email=request.args.get('email'), role=userType).first()
    if not user:
        return Response('Email not found', status=HTTPStatus.FORBIDDEN)

    if not bcrypt.check_password_hash(user.password, request.args.get('password')):
        return Response("Wrong password", status=HTTPStatus.FORBIDDEN)

    login_user(user=user)

    if returnUser:
        return UserSchema(exclude=['id','password', 'role']).dump(user)
    else:
        return Response("Login success", status=HTTPStatus.OK)

@main.route("/admin/login", methods=["POST"])
def adminLogin():
    return userLogin(UserTypes.staff)

@main.route("/customer/login", methods=["POST"])
def customerLogin():
    return userLogin(UserTypes.customer, returnUser=True)

# Admin Ebooks Management
@main.route("/admin/ebook", methods=["POST"])
@role_required(UserTypes.staff)
def postEbookAsAdmin():
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

@main.route("/admin/ebook/<int:id>", methods=["GET"])
@role_required(UserTypes.staff)
def getEbookWithIDAsAdmin(id):
    return getEbookWithID(id)

@main.route("/admin/ebook", methods=["GET"])
@role_required(UserTypes.staff)
def getAllEbookAsAdmin():
    return getAllEbook()

@main.route("/admin/ebook/<int:id>", methods=["PUT"])
@role_required(UserTypes.staff)
def putEbookWithIDAsAdmin(id):
    ebook = Ebook.query.filter_by(id=id).first()
    ebook.judul=request.args.get('judul')
    ebook.penulis=request.args.get('penulis')
    ebook.sinopsis=request.args.get('sinopsis')
    ebook.harga=int(request.args.get('harga'))
    ebook.image_url=request.args.get('image_url')
    ebook.content_url=request.args.get('content_url')

    db.session.commit()

    return EbookSchema().dump(ebook)

@main.route("/admin/ebook/<int:id>", methods=["DELETE"])
@role_required(UserTypes.staff)
def deleteEbookWithIDAsAdmin(id):
    ebook = Ebook.query.filter_by(id=id).first()
    if ebook:
        db.session.delete(ebook)
        db.session.commit()
        return Response(status=HTTPStatus.OK)

    return Response(status=HTTPStatus.NOT_FOUND)

# Customer Orders Management
@main.route("/customer/orders", methods=["GET"])
@role_required(UserTypes.customer)
def getCustomerOrders():
    orders = Order.query.filter_by(customer_id=current_user.id).all()
    return jsonify(OrderSchema(many=True).dump(orders))

@main.route("/order", methods=["POST"])
@role_required(UserTypes.customer)
def postOrder():
    order = Order(
        customer_id = current_user.id,
        ebook_id = request.args.get('id_buku'),
        harga=Ebook.query.filter_by(id=request.args.get('id_buku')).first().harga
    )

    try:
        db.session.add(order)
        db.session.commit()
    except Exception as err:
        return Response(f'{err}', status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return Response("Order successfully placed", status=HTTPStatus.OK)


# Extras
@main.route("/logout", methods=["GET"])
@login_required
def userLogout():
    logout_user()
    return Response('user logged out', status=HTTPStatus.OK)

@main.route("/whoami", methods=["GET"])
@login_required
def userWhoami():
    return Response(str(current_user), status=HTTPStatus.OK)
