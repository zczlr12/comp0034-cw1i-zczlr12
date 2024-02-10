from src.models import Item, Data
from src import db, ma


# Flask-Marshmallow Schemas
# See https://marshmallow-sqlalchemy.readthedocs.io/en/latest/#generate-marshmallow-schemas

class ItemSchema(ma.SQLAlchemyAutoSchema):
    """Marshmallow schema defining the attributes for creating a new region."""

    class Meta:
        model = Item
        load_instance = True
        sqla_session = db.session
        include_relationships = True


class DataSchema(ma.SQLAlchemyAutoSchema):
    """Marshmallow schema for the attributes of a data class. Inherits all the attributes from the Data class."""

    class Meta:
        model = Data
        include_fk = True
        load_instance = True
        sqla_session = db.session
        include_relationships = True