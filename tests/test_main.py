from flaskr.models import User, Ebook
from flaskr.schema import EbookSchema, UserSchema
from flaskr.schema import UserTypes
from flask.testing import FlaskClient

from flask import jsonify
from flask_login import current_user
from http import HTTPStatus
import pytest
from werkzeug.test import TestResponse

def test_setup_success(client):
    response = client.get("/")
    assert response.data == b'Hello, World!'

def test_register_staff_requires(client):
    """Assert staff register warnings given incomplete argument"""
    response = client.post("/admin/register")
    assert response.data == b"{'name': ['Missing data for required field.'], 'email': ['Missing data for required field.'], 'phone_number': ['Missing data for required field.'], 'address': ['Missing data for required field.'], 'password': ['Missing data for required field.']}"

data_staff_A = {
    "name": "staff name A",
    "email": "staff_a@example.com",
    "phone_number": "+628123456789",
    "address": "staff A's home, city A",
    "password": "staff_a_secret_password",
}

data_customer_A = {
    "name": "customer name A",
    "email": "customer_a@example.com",
    "phone_number": "+628987654321",
    "address": "customer A's home, city A",
    "password": "customer_a_secret_password",
}

data_ebook_A = {
    "judul":"judul_A", 
    "penulis":"penulis_A", 
    "sinopsis":"sinopsis_A", 
    "harga": 1234, 
    "image_url":"image_url_A", 
    "content_url":"content_url_A", 
}

@pytest.mark.usefixtures("client")
class TestWithFixtures:
    @staticmethod
    def _test_register_user(client: FlaskClient, user_type: UserTypes, user_data: dict):
        route = get_route(user_type)

        #  WHEN arguments incomplete THEN error missing data for required fields
        response = client.post(route+"/register")
        assert response.data == b"{'name': ['Missing data for required field.'], 'email': ['Missing data for required field.'], 'phone_number': ['Missing data for required field.'], 'address': ['Missing data for required field.'], 'password': ['Missing data for required field.']}"
        
        #  WHEN arguments complete THEN register succcess
        response = client.post(route+"/register", query_string=user_data)
        assert response.data == b"Registration success"
        # Asserts user exists in database
        user = User.query.filter_by(email=user_data["email"]).first()
        assert user.name == user_data["name"]
        assert user.email == user_data["email"]
        assert "+" + str(user.phone_number.country_code) == user_data["phone_number"][:3]
        assert str(user.phone_number.national_number) == user_data["phone_number"][3:]
        assert user.address == user_data["address"]
        assert user.password != user_data["password"] # The password in database should be encrypted
        assert user.role == user_type # assert role

        # WHEN arguments complete but email already exists THEN error duplicate email
        response = client.post(route+"/register", query_string=data_staff_A)
        assert response.data == b"This email already exists"

    @staticmethod
    def _test_login_user(client: FlaskClient, user_type: UserTypes, user_data: dict):
        """Assert admin login functionalities"""
        # asserts mail not found
        response = login_user(client, 
            user_email="wrong_email@wrong.foo", 
            user_password=user_data["password"],
            user_type=user_type)
        assert response.data == b"Email not found"

        # asserts wrong password
        response = login_user(client, 
            user_email=user_data["email"], 
            user_password="a_wrong_password",
            user_type=user_type)
        assert response.data == b"Wrong password"

        # asserts successful login
        response = login_user(client, 
            user_email=user_data["email"], 
            user_password=user_data["password"],
            user_type=user_type)

        if user_type == UserTypes.staff:
            assert response.data == b"Login success"
        elif user_type == UserTypes.customer:
            assert response.data == jsonify(UserSchema(exclude=['id','password', 'role']).dump(current_user)).data
        else:
            assert False
        # assert current user in client session
        assert current_user.email == user_data["email"]
        assert current_user.role == user_type

    def test_staff_register(self, client: FlaskClient):
        """Assert '/admin/register' functionalities"""
        self._test_register_user(client, UserTypes.staff, data_staff_A)

    def test_customer_register(self, client: FlaskClient):
        """Assert '/customer/register' functionalities"""
        self._test_register_user(client, UserTypes.customer, data_customer_A)

    def test_staff_login(self, client: FlaskClient):
        """Assert '/admin/login' functionalities"""
        self._test_login_user(client, UserTypes.staff, data_staff_A)

    def test_customer_login(self, client: FlaskClient):
        """Assert '/customer/login' functionalities"""
        self._test_login_user(client, UserTypes.customer, data_customer_A)

    def test_staff_ebook_management(self, client: FlaskClient):
        """Assert admin login & ebook management functionalities
        """
        # Assert unauthorized access to /admin/ebook/* routes
        response: TestResponse = client.get("/admin/ebook")
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        response: TestResponse = client.post("/admin/ebook")
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        response: TestResponse = client.get("/admin/ebook/1")
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        response: TestResponse = client.put("/admin/ebook/1")
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        response: TestResponse = client.delete("/admin/ebook/1")
        assert response.status_code == HTTPStatus.UNAUTHORIZED

        # login user
        response = login_user(client, 
            user_email=data_staff_A["email"], 
            user_password=data_staff_A["password"],
            user_type=UserTypes.staff)
        assert response.data == b"Login success"

        # tests adding a book
        response: TestResponse = client.post("/admin/ebook", query_string=data_ebook_A)
        # assert it exists
        ebook_A = Ebook.query.filter_by(judul=data_ebook_A["judul"]).first()
        data_ebook_A["id"] = ebook_A.id
        assert EbookSchema().dump(ebook_A) == data_ebook_A

        # tests getting list of book
        response: TestResponse = client.get(f"/admin/ebook")
        assert response.data == jsonify(EbookSchema(many=True).dump([ebook_A])).data

        # tests getting book by id
        response: TestResponse = client.get(f"/admin/ebook/{data_ebook_A['id']}")
        assert response.data == jsonify(EbookSchema().dump(ebook_A)).data

        response: TestResponse = client.get(f"/admin/ebook/9999999999")
        assert response.data == b'{}\n'

        # tests update book by id
        data_ebook_A.update({
            "judul":"updated_judul_A", 
            "penulis":"updated_penulis_A", 
            "sinopsis":"updated_sinopsis_A", 
            "harga": 12345678,
            "image_url":"updated_image_url_A", 
            "content_url":"updated_content_url_A"
        })
        response: TestResponse = client.put(f"/admin/ebook/{data_ebook_A['id']}", 
            query_string=data_ebook_A)
        assert response.data == jsonify(EbookSchema().dump(ebook_A)).data

        # tests delete book by id
        response: TestResponse = client.delete(f"/admin/ebook/{data_ebook_A['id']}")
        assert response.status_code == HTTPStatus.OK
        ebook_A = Ebook.query.filter_by(id=data_ebook_A["id"]).first()
        assert not ebook_A

def get_route(user_type: UserTypes):
    if user_type == UserTypes.staff:
        route = "/admin"
    elif user_type == UserTypes.customer:
        route = "/customer"
    else:
        assert False

    return route

def login_user(client, user_email, user_password, user_type):
    """Login user in a client context

    Args:
        client: pytest fixture of test_client
        user_email
        user_password
    Returns:
        response
    """
    route = get_route(user_type)
    response = client.post(route+"/login", query_string={
            "email": user_email,
            "password": user_password,
        })
    return response
