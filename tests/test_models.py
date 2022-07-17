"""
Test cases for Product Model

"""
# from itertools import product
# from math import prod
from itertools import product
import os
import logging
import unittest

# from sqlalchemy import true
from sqlalchemy import null
from werkzeug.exceptions import NotFound
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
        )
        self.assertEqual(str(product), "<Product 'shirt' id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "shirt")
        self.assertEqual(product.category, "men's clothing")
        self.assertEqual(product.available, True)
        self.assertEqual(product.description, "relaxed")
        self.assertEqual(product.price, 20.0)
        self.assertEqual(product.rating, None)
        self.assertEqual(product.cumulative_ratings, None)
        self.assertEqual(product.no_of_users_rated, None)

    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        product.create()
        self.assertEqual(len(Product.all()), 1)
        # delete the product and make sure it isn't in the database
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductFactory()
        logging.debug(product)
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Fetch it back
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.category, product.category)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)
        self.assertEqual(found_product.available, product.available)
        self.assertEqual(found_product.rating, product.rating)
        self.assertEqual(found_product.cumulative_ratings, product.cumulative_ratings)
        self.assertEqual(found_product.no_of_users_rated, product.no_of_users_rated)

    def test_list_all_products(self):
        """It should List all Products in the database"""
        products = Product.all()
        self.assertEqual(products, [])
        # Create 5 Products
        for i in range(5):
            product = ProductFactory()
            product.create()
        # See if we get back 5 products
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_product(self):
        """It should Find a Product by ID"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        logging.debug(products)
        # make sure they got saved
        self.assertEqual(len(Product.all()), 5)
        # find the 2nd product in the list
        product = Product.find(products[1].id)
        self.assertIsNot(product, None)
        self.assertEqual(product.id, products[1].id)
        self.assertEqual(product.name, products[1].name)
        self.assertEqual(product.category, products[1].category)
        self.assertEqual(product.description, products[1].description)
        self.assertEqual(product.price, products[1].price)
        self.assertEqual(product.available, products[1].available)
        self.assertAlmostEqual(product.rating, products[1].rating)
        self.assertEqual(product.cumulative_ratings, products[1].cumulative_ratings)
        self.assertEqual(product.no_of_users_rated, products[1].no_of_users_rated)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = Product(
            name="shirt",
            category="women's clothing",
            available=True,
            price=15.0,
            description="Relaxed Fit",
        )
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)

    def test_update_a_product(self):
        """It should Update a Product"""
        product = ProductFactory()
        logging.debug(product)
        product.id = None
        product.create()
        logging.debug(product)
        self.assertIsNotNone(product.id)
        # Change it an save it
        product.category = "k9"
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.category, "k9")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].category, "k9")

    def test_update_no_id(self):
        """It should not Update a Product with no id"""
        product = ProductFactory()
        logging.debug(product)
        product.id = None
        self.assertRaises(DataValidationError, product.update)

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
        self.assertIn("cumulative_ratings",data)
        self.assertEqual(data["cumulative_ratings"], product.cumulative_ratings)
        self.assertIn("no_of_users_rated", data)
        self.assertEqual(data["no_of_users_rated"], product.no_of_users_rated)

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
        self.assertEqual(product.cumulative_ratings, data["cumulative_ratings"])
        self.assertEqual(product.no_of_users_rated, data["no_of_users_rated"])

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

    def test_deserialize_bad_cumulative_rating(self):
        '''It should not deserialize a bad cumulative rating attribute'''
        test_product = ProductFactory()
        data = test_product.serialize()
        data["cumulative_ratings"] = "string"
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_neg_cumulative_rating(self):
        '''It should not deserialize a negative a cumulative data'''
        test_product = ProductFactory()
        data = test_product.serialize()
        data["cumulative_ratings"] = -1
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_no_of_users(self):
        '''It should not deserialize a bad no of users who rated a product'''
        test_product = ProductFactory()
        data = test_product.serialize()
        data["no_of_users_rated"] = "string"
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_neg_no_of_users(self):
        '''It should not deserialize a negative no of users'''
        test_product = ProductFactory()
        data = test_product.serialize()
        data["no_of_users_rated"] = -1
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_find_or_404_found(self):
        """It should Find or return 404 not found"""
        products = ProductFactory.create_batch(3)
        for product in products:
            product.create()
        product = Product.find_or_404(products[1].id)
        self.assertIsNot(product, None)
        self.assertEqual(product.id, products[1].id)
        self.assertEqual(product.name, products[1].name)
        self.assertEqual(product.category, products[1].category)
        self.assertEqual(product.description, products[1].description)
        self.assertEqual(product.price, products[1].price)
        self.assertEqual(product.available, products[1].available)
        self.assertEqual(product.rating, products[1].rating)

    def test_find_by_name(self):
        """It should Find a Product by Name"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        name = products[0].name
        found = Product.find_by_name(name)
        self.assertGreaterEqual(found.count(), 1)
        test_product = found[0]
        self.assertEqual(test_product.name, products[0].name)
        self.assertEqual(test_product.category, products[0].category)
        self.assertEqual(test_product.description, products[0].description)
        self.assertEqual(test_product.price, products[0].price)
        self.assertEqual(test_product.available, products[0].available)
        self.assertEqual(test_product.rating, products[0].rating)

    def test_find_or_404_not_found(self):
        """It should return 404 not found"""
        self.assertRaises(NotFound, Product.find_or_404, 0)

    def test_find_by_rating(self):
        """It should Find a Product by Rating"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        rating = products[0].rating
        count = len([product for product in products if product.rating is not None and product.rating >= rating])
        myCount = 0
        found = []
        if rating is not None:
            found = Product.find_by_rating(rating)
            myCount = found.count()
        self.assertEqual(myCount, count)
        for product in found:
            self.assertGreaterEqual(product.rating, rating)

    def test_find_by_category(self):
        """It should Find Products by Category"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        category = products[0].category
        count = len([product for product in products if product.category == category])
        found = product.find_by_category(category)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.category, category)

    def test_find_by_price(self):
        """It should Find a Product by Price"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        price = products[0].price
        count = len([product for product in products if product.price <= price])
        found = Product.find_by_price(price)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertGreaterEqual(price, product.price)
