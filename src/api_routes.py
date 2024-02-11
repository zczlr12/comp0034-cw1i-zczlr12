from flask import current_app as app, request, make_response, abort, jsonify
from sqlalchemy.exc import SQLAlchemyError
from marshmallow.exceptions import ValidationError
from src import db
from src.models import Item, Data
from src.schemas import ItemSchema, DetailSchema

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
