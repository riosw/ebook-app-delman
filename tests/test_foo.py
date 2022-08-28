from flaskr.models import Ebook

def test_setup_success(client):
    response = client.get("/")
    assert response.data == b'Hello, World!'

def test_register_staff(app):
    with app.app_context():
        print(Ebook.query.first())
        assert False