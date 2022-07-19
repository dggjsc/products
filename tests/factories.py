"""
Test Factory to make fake objects for testing
"""
import factory
import string
from factory.fuzzy import FuzzyChoice, FuzzyInteger, FuzzyFloat, FuzzyText
from service.models import Product, MAX_PRICE, MIN_PRICE


class ProductFactory(factory.Factory):
    """Creates fake products"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Product

    id = factory.Sequence(lambda n: n)
    name = FuzzyText(length=12, chars=string.ascii_letters)
    description = FuzzyText(length=12, chars=string.ascii_letters)
    category = FuzzyChoice(choices=["men's clothing", "women's clothing"])
    price = FuzzyFloat(MIN_PRICE, MAX_PRICE)
    available = FuzzyChoice(choices=[True, False])
