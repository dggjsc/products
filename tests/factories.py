"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyChoice, FuzzyFloat
from service.models import Product, MAX_PRICE, MIN_PRICE


class ProductFactory(factory.Factory):
    """Creates fake products"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Product

    id = factory.Sequence(lambda n: n)
    name = FuzzyChoice(choices=["shirt", "sweater", "pants", "lounge_wear"])
    description = FuzzyChoice(choices=["unavailable", "Relaxed Fit", "Slim Fit"])
    category = FuzzyChoice(choices=["men's clothing", "women's clothing"])
    price = FuzzyFloat(MIN_PRICE, MAX_PRICE)
    available = FuzzyChoice(choices=[True, False])
