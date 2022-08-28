import pytest
from flaskr import create_app, db

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True
    })

    db.init_app(app)

    # setUp
    db.create_all()

    yield app

    # teardown
    db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()
