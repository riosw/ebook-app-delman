import pytest
from flaskr import create_app, db

@pytest.fixture(scope='class')
def app():
    app = create_app()
    app.config.update({
        "TESTING": True
    })

    db.init_app(app)

    # setup
    print('$$ app fixture initiated')
    db.create_all()

    yield app

    # teardown
    db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    with app.test_client() as test_client:
        with app.app_context():
            # This is required to ensure all client usage uses the same app context
            print('$$ client fixture initiated')
            yield test_client
