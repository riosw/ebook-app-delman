from flaskr.models import User
import pytest

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

@pytest.mark.usefixtures("client")
class TestWithFixtures:
    data_staff_A = {
        "name": "staff name A",
        "email": "staff_a@example.com",
        "phone_number": "+628123456789",
        "address": "staff A's home, city A",
        "password": "staff_a_secret_password",
    }

    def test_register_staff(self, client):
        """Assert '/admin/register' functionalities
        
        WHEN arguments incomplete THEN error missing data for required fields
        """
        response = client.post("/admin/register", query_string=data_staff_A)
        assert response.data == b"Registration success"
        
        user_A = User.query.filter_by(name=data_staff_A["name"]).first()
        assert user_A.name == "staff name A"

        response = client.post("/admin/register", query_string=data_staff_A)
        assert response.data == b"This email already exists"
