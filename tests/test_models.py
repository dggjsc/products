"""
Test cases for Product Model

"""
import os
import logging
import unittest
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
    """ Test Cases for Product Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)
        # pass

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_XXXX(self):
        """ It should always be true """
        self.assertTrue(True)
    def test_serialize_a_pet(self):
        """It should serialize a Pet"""
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
    # def test_create_a_product(self):
    #     """It should Create a product and assert that it exists"""
    #     product = Product(name="Cotton-Hemp Sweater", category="sweater", available=True, gender=men)
    #     self.assertEqual(str(product), "<Product 'Cotton-Hemp Sweater' id=[None]>")
    #     self.assertTrue(product is not None)
    #     self.assertEqual(product.id, None)
    #     self.assertEqual(product.name, "Cotton-Hemp Sweater")
    #     self.assertEqual(product.category, "sweater")
    #     self.assertEqual(product.available, True)
    #     product = Product(name="Cotton-Hemp Sweater", category="sweater", available=False, gender=men)
    #     self.assertEqual(product.available, False)
