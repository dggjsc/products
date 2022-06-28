"""
Test cases for Product Model

"""
# from itertools import product
import os
import logging
import unittest

# from werkzeug.exceptions import NotFound
from service.models import Product, DataValidationError, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  Product   M O D E L   T E S T   C A S E S
######################################################################


class TestProduct(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)
        # pass

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(
            name="shirt",
            category="men's clothing",
            available=True,
            description="relaxed",
            price=20.0,
            rating=3,
        )
        self.assertEqual(str(product), "<Product 'shirt' id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "shirt")
        self.assertEqual(product.category, "men's clothing")
        self.assertEqual(product.available, True)
        self.assertEqual(product.description, "relaxed")
        self.assertEqual(product.price, 20.0)
        self.assertEqual(product.rating, 3)

    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        product.create()
        self.assertEqual(len(Product.all()), 1)
        # delete the product and make sure it isn't in the database
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_XXXX(self):
        """It should always be true"""
        self.assertTrue(True)

    def test_serialize_a_product(self):
        """It should serialize a Product"""
        product = ProductFactory()
        data = product.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], product.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], product.name)
        self.assertIn("category", data)
        self.assertEqual(data["category"], product.category)
        self.assertIn("description", data)
        self.assertEqual(data["description"], product.description)
        self.assertIn("price", data)
        self.assertEqual(data["price"], product.price)
        self.assertIn("available", data)
        self.assertEqual(data["available"], product.available)
        self.assertIn("rating", data)
        self.assertEqual(data["rating"], product.rating)

    def test_deserialize_a_product(self):
        """It should de-serialize a Product"""
        data = ProductFactory().serialize()
        product = Product()
        product.deserialize(data)
        self.assertNotEqual(product, None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, data["name"])
        self.assertEqual(product.description, data["description"])
        self.assertEqual(product.category, data["category"])
        self.assertEqual(product.price, data["price"])
        self.assertEqual(product.available, data["available"])
        self.assertEqual(product.rating, data["rating"])

    def test_deserialize_missing_data(self):
        """It should not deserialize a Product with missing data"""
        data = {"id": 1, "name": "shirt", "description": "Relaxed Fit"}
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_available(self):
        """It should not deserialize a bad available attribute"""
        test_product = ProductFactory()
        data = test_product.serialize()
        data["available"] = "true"
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_price(self):
        """It should not deserialize a bad price attribute"""
        test_product = ProductFactory()
        data = test_product.serialize()
        data["price"] = "string!"
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_Price_2(self):
        """It should not deserialize a price that exceeds the max price"""
        test_product = ProductFactory()
        data = test_product.serialize()
        data["price"] = 1000.0
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_Price_3(self):
        """It should not deserialize a price that is smaller than the min price"""
        test_product = ProductFactory()
        data = test_product.serialize()
        data["price"] = -10.0
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_Rating(self):
        """It should not deserialize a rating that is smaller than zero"""
        test_product = ProductFactory()
        data = test_product.serialize()
        data["rating"] = -10.0
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_Rating_2(self):
        """It should not deserialize a rating that is greater than five"""
        test_product = ProductFactory()
        data = test_product.serialize()
        data["rating"] = 10.0
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_Rating_3(self):
        """It should not deserialize a bad rating attribute"""
        test_product = ProductFactory()
        data = test_product.serialize()
        data["rating"] = "string!"
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    # def test_invalid_name(self):
    #     """It should not make a product with invalid name"""
    #     data = {"id": 1, "name": "shoes", "description": "Relaxed Fit", "category":"men's clothing", "available":True}
    #     product = Product()
    #     self.assertRaises(DataValidationError, , data)

    # def test_find_or_404_not_found(self):
    #     """It should return 404 not found"""
    #     self.assertRaises(NotFound, Product.find_or_404, 0)
