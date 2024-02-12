import os
import string
import secrets
from pathlib import Path
from datetime import datetime
import pytest
from faker import Faker
from sqlalchemy import exists
from src import create_app, db
from src.models import Account
from src.helpers import decode_auth_token


@pytest.fixture(scope='session')
def app():
    """Fixture that creates a test app.

    The app is created with test config parameters that include a temporary database. The app is created once for
    each test module.

    Returns:
        app A Flask app with a test config
    """
    # Location for the temporary testing database
    db_path = Path(__file__).parent.parent.joinpath('data', 'testdb.sqlite')
    test_cfg = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + str(db_path),
    }
    app = create_app(test_config=test_cfg)

    # Push an application context to bind the SQLAlchemy object to the application
    with app.app_context():
        db.create_all()

    yield app

    # clean up / reset resources
    with app.app_context():
        db.session.remove()  # Close the database session
        db.drop_all()

        # Explicitly close the database connection
        db.engine.dispose()
    # Delete the test database
    os.unlink(db_path)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def random_user_json():
    """Generates a account with random attributes for testing and returns as JSON."""
    fake = Faker()
    # Generate an eight-character alphanumeric password
    alphabet = string.ascii_letters + string.digits
    return {'username': fake.user_name(),
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'password': ''.join(secrets.choice(alphabet) for i in range(8))}


@pytest.fixture(scope='session')
def new_user(app):
    """Create a new user and add to the database.

    Adds a new User to the database and also returns the JSON for a new user.

    The scope is session as we need the user to be there throughout for testing the logged in functions.

    """
    user_json = {
        "username": "test",
        "password": "abcdefgh"
    }

    with app.app_context():
        user = Account(username=user_json["username"],
                       first_name="test",
                       last_name="test",
                       email="test@gmail.com")
        user.set_password(user_json["password"])
        db.session.add(user)
        db.session.commit()

    yield user_json

    # Remove the region from the database at the end of the test if it still exists
    with app.app_context():
        user_exists = db.session.query(exists().where(Account.username == user_json['username'])).scalar()
        if user_exists:
            db.session.delete(user)
            db.session.commit()


@pytest.fixture()
def login(client, new_user):
    """Returns login response"""
    # Login
    # If login fails then the fixture fails. It may be possible to 'mock' this instead if you want to investigate it.
    response = client.post('/login', json=new_user, content_type="application/json")
    # Get returned json data from the login function
    yield response.json


@pytest.fixture()
def comment_json(login, app):
    """Returns comment data"""
    with app.app_context():
        yield {'date': datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
               'content': Faker().paragraph(),
               'user_id': decode_auth_token(login['token'])["sub"]}
