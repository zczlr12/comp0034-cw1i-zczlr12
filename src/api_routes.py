import datetime
from flask import current_app as app, request, make_response, abort, jsonify
from sqlalchemy.exc import SQLAlchemyError
from marshmallow.exceptions import ValidationError
from src import db
from src.models import Item, Data, Account
from src.schemas import ItemSchema, DetailSchema
from src.helpers import token_required, encode_auth_token

# Flask-Marshmallow Schemas
items_schema = ItemSchema(many=True)
item_schema = ItemSchema()
detail_schema = DetailSchema()


@app.errorhandler(404)
def resource_not_found(e):
    """ Error handler for 404.

        Args:
            HTTP 404 error
        Returns:
            JSON response with the validation error message and the 404 status code
        """
    return jsonify(error=str(e)), 404


@app.errorhandler(ValidationError)
def register_validation_error(error):
    """ Error handler for marshmallow schema validation errors.

    Args:
        error (ValidationError): Marshmallow error.
    Returns:
        HTTP response with the validation error message and the 400 status code
    """
    response = error.messages
    return response, 400


@app.get("/items")
def get_items():
    """Returns a list of items and their details in JSON.

    :returns: JSON
    """
    # Select all the regions using Flask-SQLAlchemy
    all_items = db.session.execute(db.select(Item)).scalars()
    return items_schema.dump(all_items)


@app.get("/items/<int:item_id>")
def get_data(item_id):
    """ Returns data of the item with the given id in JSON.

    :param item_id: The id of the item to return
    :param type item_id: int
    :returns: JSON
    """
    try:
        data = db.session.execute(
            db.select(Item).filter_by(item_id=item_id)
        ).scalar_one_or_none()
        return detail_schema.dump(data)
    except SQLAlchemyError as e:
        # See https://flask.palletsprojects.com/en/2.3.x/errorhandling/#returning-api-errors-as-json
        abort(404, description="Region not found.")


@app.post('/items')
@token_required
def add_item():
    """ Adds a new event.
    
    Gets the JSON data from the request body and uses this to deserialise JSON to an object using Marshmallow 
    item_schema.load()

    :returns: JSON"""
    item_json = request.get_json()
    item = item_schema.load(item_json)
    db.session.add(item)
    db.session.commit()
    return {"message": f"Item added with id= {item.item_id}"}


@app.delete('/items/<int:item_id>')
@token_required
def delete_item(item_id):
    """ Deletes all data of an item.
    
    Gets data of the item from the database and deletes it.

    :returns: JSON"""
    data = db.session.execute(
        db.select(Data).filter_by(item_id=item_id)
    ).scalars()
    item = db.session.execute(
        db.select(Item).filter_by(item_id=item_id)
    ).scalar_one_or_none()
    for datum in data:
        db.session.delete(datum)
    db.session.delete(item)
    db.session.commit()
    return {"message": f"item deleted with id= {item_id}"}


@app.patch("/items/<int:item_id>")
@token_required
def data_update(item_id):
    """Updates changed fields for the item.

    """
    # Find the event in the database
    existing_item = db.session.execute(
        db.select(Item).filter_by(item_id=item_id)
    ).scalar_one_or_none()
    # Get the updated details from the json sent in the HTTP patch request
    item_json = request.get_json()
    # Use Marshmallow to update the existing records with the changes from the json
    data_updated = detail_schema.load(item_json, instance=existing_item, partial=True)
    # Commit the changes to the database
    db.session.add(data_updated)
    db.session.commit()
    # Return json showing the updated record
    updated_data = db.session.execute(
        db.select(Item).filter_by(item_id=item_id)
    ).scalar_one_or_none()
    result = detail_schema.jsonify(updated_data)
    response = make_response(result, 200)
    response.headers["Content-Type"] = "application/json"
    return response


# AUTHENTICATION ROUTES
@app.post("/register")
def register():
    """Register a new user for the REST API

    If successful, return 201 Created.
    If email already exists, return 409 Conflict (resource already exists).
    If any other error occurs, return 500 Server error
    """
    # Get the JSON data from the request
    user_json = request.get_json()
    # Check if user already exists, returns None if the user does not exist
    user = db.session.execute(
        db.select(Account).filter_by(email=user_json.get("username"))
    ).scalar_one_or_none()
    if not user:
        try:
            # Create new User object
            user = Account(username=user_json.get("username"),
                           first_name=user_json.get("first_name"),
                           last_name=user_json.get("last_name"),
                           email=user_json.get("email"))
            # Set the hashed password
            user.set_password(password=user_json.get("password"))
            # Add user to the database
            db.session.add(user)
            db.session.commit()
            # Return success message
            response = {
                "message": "Successfully registered.",
            }
            # Log the registered user
            current_time = datetime.datetime.now(datetime.UTC)
            app.logger.info(f"{user.email} registered at {current_time}")
            return make_response(jsonify(response)), 201
        except SQLAlchemyError as e:
            app.logger.error(f"A SQLAlchemy database error occurred: {str(e)}")
            response = {
                "message": "An error occurred. Please try again.",
            }
            return make_response(jsonify(response)), 500
    else:
        response = {
            "message": "User already exists. Please Log in.",
        }
        return make_response(jsonify(response)), 409


@app.post('/login')
def login():
    """Logins in the User and generates a token

    If the email and password are not present in the HTTP request, return 401 error
    If the user is not found in the database, or the password is incorrect, return 401 error
    If the user is logged in and the token is generated, return the token and 201 Success
    """
    auth = request.get_json()

    # Check the email and password are present, if not return a 401 error
    if not auth or not auth.get('username') or not auth.get('password'):
        msg = {'message': 'Missing username or password'}
        return make_response(msg, 401)

    # Find the user in the database
    user = db.session.execute(
        db.select(Account).filter_by(email=auth.get("username"))
    ).scalar_one_or_none()

    # If the user is not found, or the password is incorrect, return 401 error
    if not user or not user.check_password(auth.get('password')):
        msg = {'message': 'Incorrect email or password.'}
        return make_response(msg, 401)

    # If all OK then create the token
    token = encode_auth_token(user.id)

    # Return the token and the user_id of the logged in user
    return make_response(jsonify({"user_id": user.id, "token": token}), 201)