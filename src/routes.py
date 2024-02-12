from datetime import datetime
from flask import json, current_app as app, request, make_response, abort, jsonify
from sqlalchemy.exc import SQLAlchemyError
from marshmallow.exceptions import ValidationError
from werkzeug.exceptions import HTTPException
from src import db
from src.models import Item, Data, Account, Comment
from src.schemas import ItemSchema, DetailSchema, CommentSchema
from src.helpers import token_required, encode_auth_token

# Flask-Marshmallow Schemas
comments_schema = CommentSchema(many=True)
comment_schema = CommentSchema()
items_schema = ItemSchema(many=True)
item_schema = ItemSchema()
detail_schema = DetailSchema()


@app.errorhandler(Exception)
def handle_non_http_exception(e):
    """Handle non-HTTP exceptions as 500 Server error in JSON format."""

    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": 500,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


@app.errorhandler(HTTPException)
def handle_http_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


# Adapted from 'Returning API Errors as JSON' at
# See https://flask.palletsprojects.com/en/2.3.x/errorhandling/#returning-api-errors-as-json
# Accessed 05/02/2023
@app.errorhandler(404)
def resource_not_found(e):
    """ Error handler for 404.

        Args:
            HTTP 404 error
        Returns:
            JSON response with the validation error message and 404
        """
    return jsonify(error=str(e)), 404


@app.errorhandler(ValidationError)
def register_validation_error(error):
    """ Error handler for marshmallow schema validation errors.

    Args:
        error (ValidationError): Marshmallow error.
    Returns:
        HTTP response with the validation error message and 400
    """
    response = error.messages
    return response, 400


# AUTHENTICATION ROUTES
@app.post("/register")
def register():
    """Register a new user for the REST API

    If successful, return 201 Created.
    If username or email already exists, return 409 Conflict.
    If any other error occurs, return 500 Server error
    """
    # Get the JSON data from the request
    user_json = request.get_json()
    # Check if user already exists, returns None if the user does not exist
    existing_username = db.session.execute(
        db.select(Account).filter_by(username=user_json.get("username"))
    ).scalar_one_or_none()
    existing_email = db.session.execute(
        db.select(Account).filter_by(email=user_json.get("email"))
    ).scalar_one_or_none()
    if not existing_username and not existing_email:
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
            current_time = datetime.now()
            app.logger.info(f"{user.username} registered at {current_time}")
            return make_response(jsonify(response)), 201
        except SQLAlchemyError as e:
            app.logger.error(f"A SQLAlchemy database error occurred: {str(e)}")
            response = {
                "message": "An error occurred. Please try again.",
            }
            return make_response(jsonify(response)), 500
    else:
        response = {
            "message": "Username or email has already been used."
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

    # Check the username and password are present, if not return a 401 error
    if not auth or not auth.get('username') or not auth.get('password'):
        msg = {'message': 'Missing username or password'}
        return make_response(msg, 401)

    # Find the user in the database
    user = db.session.execute(
        db.select(Account).filter_by(username=auth.get("username"))
    ).scalar_one_or_none()

    # If the user is not found, or the password is incorrect, return 401 error
    if not user or not user.check_password(auth.get('password')):
        msg = {'message': 'Incorrect username or password.'}
        return make_response(msg, 401)
    
    app.logger.info(f"{user.username} logged in at {datetime.now()}")

    # If all OK then create the token
    token = encode_auth_token(user.user_id)

    # Return the token and the user_id of the logged in user
    return make_response(jsonify({"user_id": user.user_id, "token": token}), 201)


# COMMENT ROUTES
@app.get("/comments")
def get_comments():
    """Returns a list of comments in JSON.

    :returns: JSON
    """
    # Select all the comments using Flask-SQLAlchemy
    try:
        all_comments = db.session.execute(db.select(Comment)).scalars()
        try:
            return comments_schema.dump(all_comments)
        except ValidationError as e:
            app.logger.error(f"A Marshmallow ValidationError occurred dumping all comments: {str(e)}")
            msg = {'message': "An Internal Server Error occurred."}
            return make_response(msg, 500)
    except SQLAlchemyError as e:
        app.logger.error(f"An error occurred while fetching comments: {str(e)}")
        msg = {'message': "An Internal Server Error occurred."}
        return make_response(msg, 500)


@app.post('/comments')
@token_required
def post_comment():
    """ Adds a new comment.
    
    Gets the JSON data from the request body and uses this to deserialise JSON to an object using Marshmallow 
    comment_schema.load()

    :returns: JSON"""
    comment_json = request.get_json()
    try:
        comment = comment_schema.load(comment_json)

        try:
            db.session.add(comment)
            db.session.commit()
            return {"message": f"Comment added with id= {comment.comment_id}"}
        except SQLAlchemyError as e:
            app.logger.error(f"An error occurred saving the comment: {str(e)}")
            msg = {'message': "An Internal Server Error occurred."}
            return make_response(msg, 500)
    
    except ValidationError as e:
        app.logger.error(f"A Marshmallow ValidationError loading the comment: {str(e)}")
        msg = {'message': "The Region details failed validation."}
        return make_response(msg, 400)


# ITEM ROUTES
@app.get("/items")
def get_items():
    """Returns a list of items and their details in JSON.

    :returns: JSON
    """
    try:
        # Select all the items using Flask-SQLAlchemy
        all_items = db.session.execute(db.select(Item)).scalars()
        try:
            return items_schema.dump(all_items)
        except ValidationError as e:
            app.logger.error(f"A Marshmallow ValidationError occurred dumping all items: {str(e)}")
            msg = {'message': "An Internal Server Error occurred."}
            return make_response(msg, 500)
    except SQLAlchemyError as e:
        app.logger.error(f"An error occurred while fetching items: {str(e)}")
        msg = {'message': "An Internal Server Error occurred."}
        return make_response(msg, 500)


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
        ).scalar_one()
        return detail_schema.dump(data)
    except SQLAlchemyError as e:
        app.logger.error(f"A SQLAlchemy database error occurred: {str(e)}")
        abort(404, description="Item not found.")


@app.post('/items')
@token_required
def add_item():
    """ Adds a new event.
    
    Gets the JSON data from the request body and uses this to deserialise JSON to an object using Marshmallow 
    item_schema.load()

    :returns: JSON"""
    item_json = request.get_json()
    try:
        item = item_schema.load(item_json)

        try:
            db.session.add(item)
            db.session.commit()
            return {"message": f"Item added with id= {item.item_id}"}
        except SQLAlchemyError as e:
            app.logger.error(f"An error occurred saving the item: {str(e)}")
            msg = {'message': "An Internal Server Error occurred."}
            return make_response(msg, 500)
        
    except ValidationError as e:
        app.logger.error(f"A Marshmallow ValidationError loading the item: {str(e)}")
        msg = {'message': "The Region details failed validation."}
        return make_response(msg, 400)


@app.delete('/items/<int:item_id>')
@token_required
def delete_item(item_id):
    """ Deletes all data of an item.
    
    Gets data of the item from the database and deletes it.

    :returns: JSON"""
    try:
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
        return {"message": f"The item with id {item_id} has been deleted"}
    except SQLAlchemyError as e:
        app.logger.error(f"The item with id {item_id} does not exist. Error: {str(e)}")
        return abort(404, description="Item not found.")


@app.patch("/items/<int:item_id>")
@token_required
def data_update(item_id):
    """Updates changed fields for the item.

    """
    app.logger.error("Started the patch")
    try:
        # Find the item in the database
        existing_item = db.session.execute(
            db.select(Item).filter_by(item_id=item_id)
        ).scalar_one_or_none()
    except SQLAlchemyError as e:
        app.logger.error(f"The item with id {item_id} does not exist. Error: {str(e)}")
        return abort(404, description="Item not found.")
    # Get the updated details from the json sent in the HTTP patch request
    item_json = request.get_json()
    app.logger.error(f"item_json: {str(item_json)}")
    # Use Marshmallow to update the existing records with the changes from the json
    try:
        data_updated = detail_schema.load(item_json, instance=existing_item, partial=True)
    except ValidationError as e:
        app.logger.error(f"A Marshmallow schema validation error occurred: {str(e)}")
        msg = "Failed Marshmallow schema validation"
        return make_response(msg, 500)
    # Commit the changes to the database
    try:
        db.session.add(data_updated)
        db.session.commit()
        return {"message": f"Item with id {item_id} updated."}
    except SQLAlchemyError as e:
        app.logger.error(f"A SQLAlchemy database error occurred: {str(e)}")
        msg = "An Internal Server Error occurred."
        return make_response(msg, 500)
