import os
import re
import csv
from datetime import datetime
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
ma = Marshmallow()


def add_data_from_csv():
    """Adds data to the database if it does not already exist."""

    # Add import here and not at the top of the file to avoid circular import issues
    from src.models import Item, Data

    # If there are no data in the database, then add them
    first_item = db.session.execute(db.select(Item)).first()
    if not first_item:
        print("Start adding data to the database")
        data_file = Path(__file__).parent.parent.joinpath("data", "dataset_prepared.csv")
        with open(data_file, 'r') as file:
            csv_reader = csv.reader(file)
            header = next(csv_reader)  # Skip header row
            for col in range(1, len(header), 2):
                name = header[col].split("_", 1)[-1]
                brand_number = re.search(r'\d+', name).group()
                item_number = re.search(r'\d+$', name).group()
                i = Item(name=name,
                         brand_number=brand_number,
                         item_number=item_number)
                db.session.add(i)
            for row in csv_reader:
                for col in range(1, len(row), 2):
                    d = Data(date=datetime.strptime(row[0], "%Y-%m-%d"),
                             quantity=row[col],
                             promotion=int(row[col+1]),
                             item_id=(col+1)/2)
                    db.session.add(d)
            db.session.commit()


def create_app(test_config=None):
    # create the Flask app
    app = Flask(__name__, instance_relative_config=True)
    # configure the Flask app (see later notes on how to generate your own SECRET_KEY)
    app.config.from_mapping(
        SECRET_KEY='blo5jfo8jYiEuau4ddOqvA',
        # Set the location of the database file called paralympics.sqlite which will be in the app's instance folder
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, 'database.sqlite')
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialise Flask with the SQLAlchemy database extension
    db.init_app(app)
    ma.init_app(app)

    with app.app_context():
        db.create_all()
        # Add the data to the database if not already added
        add_data_from_csv()
        # Register the routes with the app in the context
        from src import api_routes

    return app

from src.models import Account, Comment, Item, Data