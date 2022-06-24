"""
Test Factory to make fake objects for testing
"""
import factory
# from datetime import date
from factory.fuzzy import FuzzyChoice  # FuzzyDate
# from faker import Faker
# from faker.providers import DynamicProvider
from service.models import Product, MAX_PRICE, MIN_PRICE
import random


class ProductFactory(factory.Factory):
    """Creates fake products"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Product

    id = factory.Sequence(lambda n: n)
    name = FuzzyChoice(choices=["shirt", "sweater", "pants", "lounge_wear"])
    description = FuzzyChoice(choices=["unavailable", "Relaxed Fit", "Slim Fit"])
    category = FuzzyChoice(choices=["men's clothing", "women's clothing"])
    price = round(random.uniform(MIN_PRICE, MAX_PRICE), 2)
    available = FuzzyChoice(choices=[True, False])
