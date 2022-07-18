"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase

# from unittest.mock import MagicMock, patch
from service import app
from service.models import Product
from service.models import db
from service.routes import init_db
from service.utils import status
from tests.factories import ProductFactory  # HTTP Status Codes
from urllib.parse import quote_plus
from random import *

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/products"
CONTENT_TYPE_JSON = "application/json"


######################################################################
#  T E S T   P R O D U C T  S E R V I C E
######################################################################
class TestYourResourceServer(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        self.client = app.test_client()
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    def _create_products(self, count):
        """Factory method to create products in bulk"""
        products = []
        for _ in range(count):
            test_product = ProductFactory()
            response = self.client.post(
                BASE_URL, json=test_product.serialize(), content_type=CONTENT_TYPE_JSON
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test product",
            )
            new_product = response.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)
        return products

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################
    def test_index(self):
        """It should call the Home Page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], "Product REST API Service")
        self.assertEqual(data["version"], "1.0")
        self.assertEqual(data["paths"], "http://localhost/products")

    def test_get_product_list(self):
        """It should Get a list of Products"""
        self._create_products(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_get_product_not_found(self):
        """It should not Get a Product thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_create_product(self):
        """It should Create a new Product"""
        test_product = ProductFactory()
        logging.debug("Test Product: %s", test_product.serialize())
        response = self.client.post(
            BASE_URL, json=test_product.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_product = response.get_json()
        self.assertEqual(new_product["name"], test_product.name)
        self.assertEqual(new_product["category"], test_product.category)
        self.assertEqual(new_product["description"], test_product.description)
        self.assertEqual(new_product["price"], test_product.price)
        self.assertEqual(new_product["available"], test_product.available)
        self.assertEqual(new_product["rating"], test_product.rating)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_product = response.get_json()
        self.assertEqual(new_product["name"], test_product.name)
        self.assertEqual(new_product["category"], test_product.category)
        self.assertEqual(new_product["description"], test_product.description)
        self.assertEqual(new_product["price"], test_product.price)
        self.assertEqual(new_product["available"], test_product.available)
        self.assertEqual(new_product["rating"], test_product.rating)

    def test_delete_product(self):
        """It should Delete a Product"""
        test_product = self._create_products(1)[0]
        print(test_product)
        response = self.client.delete(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # #####################################################################
    def test_get_product(self):
        """It should return a single product"""
        test_product = self._create_products(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_product.name)

    def test_update_product(self):
        """It should Update an existing Product"""
        # create a product to update
        test_product = ProductFactory()
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the product
        new_product = response.get_json()
        logging.debug(new_product)
        new_product["category"] = "unknown"
        response = self.client.put(f"{BASE_URL}/{new_product['id']}", json=new_product)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_product = response.get_json()
        self.assertEqual(updated_product["category"], "unknown")

    def test_update_product_no_id_found(self):
        """It should return 404 if update a product with the id not found"""
        # create a product to update
        test_product = ProductFactory()
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update a not exist id
        new_product = response.get_json()
        logging.debug(new_product)
        new_product["category"] = "unknown"
        wrong_id = new_product["id"] + 1
        response = self.client.put(f"{BASE_URL}/{wrong_id}", json=new_product)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_list_by_rating(self):
        """It should Query Products by Rating"""
        products = self._create_products(10)
        for product in products:
            product.no_of_users_rated = randint(1,10)
            product.cumulative_ratings = 0
            for x in range(product.no_of_users_rated):
                product.cumulative_ratings += randint(1, 5)
            product.rating = product.cumulative_ratings
            product.rating = product.rating / product.no_of_users_rated
            response = self.client.get(
                f"{BASE_URL}/{product.id}"
            )
            old_product = response.get_json()
            logging.debug(old_product)
            old_product["rating"] = product.rating
            old_product["cumulative_ratings"] = product.cumulative_ratings
            old_product["no_of_users_rated"] = product.no_of_users_rated
            response = self.client.put(f"{BASE_URL}/{old_product['id']}", json=old_product)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        test_rating = products[0].rating
        rating_products = [product for product in products if product.rating is not None and product.rating >= test_rating]
        if test_rating is not None:
            response = self.client.get(
                BASE_URL,
                query_string=f"rating={str(test_rating)}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.get_json()
            self.assertEqual(len(data), len(rating_products))

    def test_query_list_by_price(self):
        """It should Query Products by Price"""
        products = self._create_products(10)
        test_price = products[0].price
        price_products = [product for product in products if product.price <= test_price]
        response = self.client.get(
            BASE_URL,
            query_string=f"price={str(test_price)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(price_products))

    def test_first_rating_product(self):
        '''It updates the rating of the product'''
        test_product = ProductFactory()
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_product = response.get_json()
        self.assertEqual(new_product["rating"], None)
        myJson = {}
        myJson["rating"] = 3
        response = self.client.put(f"{BASE_URL}/{new_product['id']}/rating", json=myJson)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_product = response.get_json()
        self.assertAlmostEqual(new_product["rating"],3)


    ######################################################################
    #  T E S T   S A D   P A T H S
    ######################################################################

    def test_create_product_no_data(self):
        """It should not Create a Product with missing data"""
        response = self.client.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_no_content_type(self):
        """It should not Create a Product with no content type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_product_bad_available(self):
        """It should not Create a Product with bad available data"""
        test_product = ProductFactory()
        logging.debug(test_product)
        # change available to a string
        test_product.available = "yes"
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_bad_price_1(self):
        """It should not Create a Product with the price data smaller than minimum price"""
        test_product = ProductFactory()
        logging.debug(test_product)
        # change price to a price which is not in the specified range
        test_product.price = -5.0
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_bad_price_2(self):
        """It should not Create a Product with the price greater than maximum"""
        test_product = ProductFactory()
        logging.debug(test_product)
        # change price to a price which is not in the specified range
        test_product.price = 1000.0
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_bad_price_3(self):
        """It should not Create a Product with bad price data"""
        test_product = ProductFactory()
        logging.debug(test_product)
        # change price to a price which is not in the specified range
        test_product.price = "string"
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_bad_rating_1(self):
        """It should not Create a Product with the rating data smaller than minimum price"""
        test_product = ProductFactory()
        logging.debug(test_product)
        # change price to a price which is not in the specified range
        test_product.rating = -5.0
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_bad_rating_2(self):
        """It should not Create a Product with the rating greater than maximum"""
        test_product = ProductFactory()
        logging.debug(test_product)
        # change price to a price which is not in the specified range
        test_product.rating = 6
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_bad_rating_3(self):
        """It should not Create a Product with bad rating data"""
        test_product = ProductFactory()
        logging.debug(test_product)
        # change price to a price which is not in the specified range
        test_product.price = "string"
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_product_no_product(self):
        """The Product with this index doesn't exist"""
        invalid_index = -1
        response = self.client.get(f"{BASE_URL}/{invalid_index}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_method_not_allowed_put(self):
        """ It should Handle PUT request for /products with 405_METHOD_NOT_ALLOWED"""
        resp = self.client.put('/products')
        self.assertEqual(
            resp.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_method_not_allowed_get(self):
        """ It should Handle GET request for /products with 405_METHOD_NOT_ALLOWED"""
        resp = self.client.put('/products')
        self.assertEqual(
            resp.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_method_not_allowed_delete(self):
        """ It should Handle DELETE request for /products with 405_METHOD_NOT_ALLOWED"""
        resp = self.client.put('/products')
        self.assertEqual(
            resp.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_query_product_list_by_bad_rating(self):
        """It should return a 406_NOT_ACCEPTABLE error if query a bad rating"""
        response = self.client.get(
            BASE_URL,
            query_string="rating=9.2"
        )
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        response = self.client.get(
            BASE_URL,
            query_string="rating=good"
        )
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_query_product_list_by_category(self):
        """It should Query Products by Category"""
        products = self._create_products(10)
        test_category = products[0].category
        category_products = [product for product in products if product.category == test_category]
        response = self.client.get(
            BASE_URL,
            query_string=f"category={quote_plus(test_category)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(category_products))
        # check the data just to be sure
        for product in data:
            self.assertEqual(product["category"], test_category)

    def test_query_product_list_by_bad_price(self):
        """It should return a 406_NOT_ACCEPTABLE error if query a bad price"""
        response = self.client.get(
            BASE_URL,
            query_string="price=expensive"
        )
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        response = self.client.get(
            BASE_URL,
            query_string="price=-23"
        )
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_user_sends_a_correct_rating(self):
        '''It should return a 200_HTTP_OK Request that the rating has been processed. User sees the updating of rating'''
        test_product = ProductFactory()
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # update the product
        new_product = response.get_json()
        logging.debug(new_product)
        myJson = {}
        myJson["rating"] = 2
        response = self.client.put(f"{BASE_URL}/{new_product['id']}/rating", json=myJson)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        myJson["rating"] = 4
        response = self.client.put(f"{BASE_URL}/{new_product['id']}/rating", json=myJson)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_product = response.get_json()
        self.assertAlmostEqual(updated_product["rating"], 3)


    
    def test_user_sends_string_rating(self):
        '''User sends a string datatype for rating. It should return Error Code : 406'''
        test_product = ProductFactory()
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        #Provide the Rating
        new_product = response.get_json()
        logging.debug(new_product)
        myJson = {}
        myJson["rating"] = "FalseRating"
        response = self.client.put(f"{BASE_URL}/{new_product['id']}/rating",json=myJson)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_user_sends_out_of_bounds_rating(self):
        '''User sends a negative_rating/out_of_bounds'''
        test_product = ProductFactory()
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        #Provide Negative Rating:
        new_product = response.get_json()
        logging.debug(new_product)
        myJson = {}
        myJson["rating"] = -1
        response = self.client.put(f"{BASE_URL}/{new_product['id']}/rating", json=myJson)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    
    def test_user_sends_rating_of_invalid_product_id(self):
        '''User sends rating to invalid product id'''
        test_product = ProductFactory()
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_product = response.get_json()
        logging.debug(new_product)
        wrong_id = new_product["id"] + 1
        myJson = {}
        myJson["rating"] = 3
        response = self.client.put(f"{BASE_URL}/{wrong_id}/rating", json=myJson)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)