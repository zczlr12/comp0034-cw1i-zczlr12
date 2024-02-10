from flask import current_app as app

from src import db
from src.models import Item, Data
from src.schemas import ItemSchema, DataSchema

# Flask-Marshmallow Schemas
items_schema = ItemSchema(many=True)
item_schema = ItemSchema()
datas_schema = DataSchema(many=True)
data_schema = DataSchema()


@app.get("/items")
def get_items():
    """Returns a list of items and their details in JSON.

    :returns: JSON
    """
    # Select all the regions using Flask-SQLAlchemy
    all_items = db.session.execute(db.select(Item)).scalars()
    # Dump the data using the Marshmallow regions schema; '.dump()' returns JSON.
    result = items_schema.dump(all_items)
    # Return the data in the HTTP response
    return result

@app.get("/datas")
def get_datas():
    """Returns a list of items and their details in JSON.

    :returns: JSON
    """
    # Select all the datas using Flask-SQLAlchemy
    all_datas = db.session.execute(db.select(Data)).scalars()
    # Dump the data using the Marshmallow datas schema; '.dump()' returns JSON.
    result = datas_schema.dump(all_datas)
    # Return the data in the HTTP response
    return result