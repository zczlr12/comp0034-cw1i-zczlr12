from src.models import Account, Comment, Item, Data
from src import db, ma


# Flask-Marshmallow Schemas
# See https://marshmallow-sqlalchemy.readthedocs.io/en/latest/#generate-marshmallow-schemas

class AccountSchema(ma.SQLAlchemySchema):
    """Marshmallow schema defining the attributes for creating a new account."""

    class Meta:
        model = Account
        load_instance = True
        sqla_session = db.session
        include_relationships = True

    user_id = ma.auto_field()
    username = ma.auto_field()
    password_hash = ma.auto_field()
    first_name = ma.auto_field()
    last_name = ma.auto_field()
    email = ma.auto_field()


class CommentSchema(ma.SQLAlchemyAutoSchema):
    """Marshmallow schema defining the attributes for creating a new comment."""

    class Meta:
        model = Comment
        load_instance = True
        sqla_session = db.session
        include_relationships = True


class ItemSchema(ma.SQLAlchemySchema):
    """Marshmallow schema defining the attributes for creating a new item."""

    class Meta:
        model = Item
        load_instance = True
        sqla_session = db.session
        include_relationships = True

    item_id = ma.auto_field()
    name = ma.auto_field()
    brand_number = ma.auto_field()
    item_number = ma.auto_field()


class DataSchema(ma.SQLAlchemySchema):
    """Marshmallow schema for the attributes of a data class. Inherits all the attributes from the Data class."""

    class Meta:
        model = Data
        include_fk = True
        load_instance = True
        sqla_session = db.session
        include_relationships = True
    
    date = ma.auto_field()
    quantity = ma.auto_field()
    promotion = ma.auto_field()


class DetailSchema(ma.SQLAlchemyAutoSchema):
    """Marshmallow schema for the detail of a item class. Inherits all the attributes from the Data class."""

    class Meta:
        model = Item
        include_fk = True
        load_instance = True
        sqla_session = db.session
        include_relationships = True

    data = ma.Nested(DataSchema, many=True)
