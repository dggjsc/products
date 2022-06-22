"""
Models for Product

All of the models are stored in this module
"""
import logging
from unicodedata import category
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()
def init_db(app):
    """Initialize the SQLAlchemy app"""
    Product.init_db(app)

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

    pass

class Product(db.Model):
    """
    Class that represents a product
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    description = db.Column(db.String(63), nullable=True, server_default=("unavailable"))
    category = db.Column(db.String(63), nullable=False)
    price = db.Column(db.Float(),nullable=False)
    available = db.Column(db.Boolean(), nullable=False, default=False)

    def __repr__(self):
        return "<Product %r id=[%s]>" % (self.name, self.id)

    def create(self):
        """
        Creates a product to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a product to the database
        """
        logger.info("Saving %s", self.name)
        db.session.commit()

    def delete(self):
        """ Removes a product from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a product into a dictionary """
        return {"id": self.id, 
                "name": self.name,
                "description": self.description,
                 "category": self.category,
                 "price": self.price,
                 "available": self.available
                 }

    def deserialize(self, data):
        """
        Deserializes a product from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.description = data["description"]
            self.category = data["category"]
            if isinstance(data["price"], float):  
                self.price = data["price"]
            else:
                raise DataValidationError(
                    "Invalid type for float [price]: "
                    + str(type(data["price"]))
                )
            if isinstance(data["available"], bool):
                self.available = data["available"]
            else:
                raise DataValidationError(
                    "Invalid type for boolean [available]: "
                    + str(type(data["available"]))
                )
        except KeyError as error:
            raise DataValidationError(
                "Invalid product: missing " + error.args[0]
            )
        except TypeError as error:
            raise DataValidationError(
                "Invalid product: body of request contained bad or no data"
            )
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the products in the database """
        logger.info("Processing all products")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a product by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get_or_404(by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all products with the given name

        Args:
            name (string): the name of the products you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
