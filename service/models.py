"""
Models for Product

All of the models are stored in this module
"""
import logging
from wsgiref import validate
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
MAX_PRICE=10.00
MIN_PRICE=100.00

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()
def init_db(app):
    """Initialize the SQLAlchemy app"""
    Product.init_db(app)
# Defining acceptable input for names and descriptions
def acceptable_names():
    return ["shirt", "sweater", "pants", "lounge_wear"]
def acceptable_description():
    return ["unavailable", "Relaxed Fit", "Slim Fit"]
class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

class Product(db.Model):
    """
    Class that represents a product
    """
    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    description = db.Column(db.String(63), nullable=True, server_default=("unavailable"))
    category = db.Column(db.String(63), nullable=False)
    price = db.Column(db.Float(),nullable=False)
    available = db.Column(db.Boolean(), nullable=False, default=False)
    # Just an Idea to test for correct input. delete the function later if it's not used
    def validate_product(self):
        if self.name not in acceptable_names:
            raise DataValidationError("Invalid Name")
        elif self.description not in acceptable_description:
            raise DataValidationError("Invalid Description")
        elif self.price < MIN_PRICE or self.price > MAX_PRICE:
            raise DataValidationError("Price is not within the range")
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
        Updates a Pet to the database
        """
        logger.info("Saving %s", self.name)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """ Removes a product from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self) -> dict:
        """ Serializes a product into a dictionary """
        return {"id": self.id, 
                "name": self.name,
                "description": self.description,
                 "category": self.category,
                 "price": self.price,
                 "available": self.available
                 }

    def deserialize(self, data: dict):
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
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0])
        except KeyError as error:
            raise DataValidationError("Invalid product: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid YourResourceModel: body of request contained bad or no data - "
                "Error message: " + error
            )
        return self

##################################################
# CLASS METHODS
##################################################
    @classmethod
    def init_db(cls, app: Flask):
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
    def find_or_404(cls, product_id: int):
        """Find a Pet by it's id

        :param pet_id: the id of the Pet to find
        :type pet_id: int

        :return: an instance with the pet_id, or 404_NOT_FOUND if not found
        :rtype: Pet

        """
        logger.info("Processing lookup or 404 for id %s ...", product_id)
        return cls.query.get_or_404(product_id)
    @classmethod
    def find_by_name(cls, name):
        """Returns all products with the given name

        Args:
            name (string): the name of the products you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
