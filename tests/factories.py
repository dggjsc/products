"""
Test Factory to make fake objects for testing
"""
import factory
# from datetime import date
from factory.fuzzy import FuzzyChoice, FuzzyDate
from faker import Faker
from faker.providers import DynamicProvider
from service.models import Product
import random

MIN_PRICE = 10.00
MAX_PRICE = 300.00
# pants = DynamicProvider(
#      provider_name="pants",
#      elements=["Jeans", "Jogger", "dress pants", "pajamas"],
# )
# sweater = DynamicProvider(
#     provider_name="sweater",
#     elements=["lounge wear", "Cardigan", "Blazer", "Crew-Neck" ]
# )
# shirts = DynamicProvider(
#     provider_name="shirts"
#     elements=["Dress shirts", "Casual Shirts"]
# )
class ProductFactory(factory.Factory):
    """Creates fake products"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Product

    id = factory.Sequence(lambda n: n)
    name = FuzzyChoice(choices=["shirt", "sweater", "pants", "lounge_wear"])
    description = FuzzyChoice(choices=["unavailable", "Relaxed Fit", "Slim Fit"])
    category = FuzzyChoice(choices=["men's clothing", "women's clothing"])
    price = factory.LazyAttribute(random.randrange(MIN_PRICE, MAX_PRICE + 1))
    
    # gender = FuzzyChoice(choices=[Gender.MEN, Gender.WOMEN, Gender.UNISEX])
    available = FuzzyChoice(choices=[True, False])
