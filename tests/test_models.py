"""
Test cases for Product Model

"""
import os
import logging
import unittest
from service.models import Product, DataValidationError, db

######################################################################
#  Product   M O D E L   T E S T   C A S E S
######################################################################
class TestYourResourceModel(unittest.TestCase):
    """ Test Cases for Product Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        pass

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        pass

    def tearDown(self):
        """ This runs after each test """
        pass

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_XXXX(self):
        """ It should always be true """
        self.assertTrue(True)
    def test_create_a_pet(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Cotton-Hemp Sweater", category="clothes", available=True, description="Relaxed fit sweater with long sleeves")
        self.assertEqual(str(product), "<Product 'Cotton-Hemp Sweater' id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fido")
        self.assertEqual(product.category, "dog")
        self.assertEqual(product.available, True)
        self.assertEqual(product.gender, Gender.MALE)
        product = Product(name="Fido", category="dog", available=False, gender=Gender.FEMALE)
        self.assertEqual(product.available, False)
        self.assertEqual(product.gender, Gender.FEMALE)
