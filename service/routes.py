"""
My Service

Describe what your service does here
"""

# import os
# import sys
# import logging
# from flask import Flask, request, url_for, jsonify, make_response, abort
from flask import url_for, jsonify, request, abort
from service.utils import status  # HTTP Status Codes
from service.models import Product

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        # "Reminder: return some useful information in json format about the service here",
        jsonify(
            name="Product REST API Service",
            paths=url_for("list_products", _external=True),
            version="1.0",
        ),
        status.HTTP_200_OK,
    )


######################################################################
# LIST ALL PRODUCTS
######################################################################
def check_category(category):
    products = Product.find_by_category(category)
    results = [product.serialize() for product in products]
    app.logger.info("Returning %d products", len(results))
    return results


def check_price(price):
    price = float(price)
    if price < 0:
        raise ValueError
    products = Product.find_by_price(price)
    results = [product.serialize() for product in products]
    results.sort(key=lambda n: n["price"], reverse=True)
    return results


def check_rating(rating_str):
    rating = float(rating_str)
    if rating <= 0 or rating > 5:
        raise ValueError
    products = Product.find_by_rating(rating)
    results = [product.serialize() for product in products if product.rating is not None]
    results.sort(key=lambda n: n["rating"], reverse=True)
    return results


@app.route("/products", methods=["GET"])
def list_products():
    app.logger.info("Request for Product List")
    products = []
    results = []
    rating_str = request.args.get("rating")
    category = request.args.get("category")
    price = request.args.get("price")
    available = request.args.get("available")
    if category:
        results = check_category(category)
    elif price:
        try:
            results = check_price(price)
        except ValueError:
            return "", status.HTTP_406_NOT_ACCEPTABLE
    elif rating_str:
        try:
            results = check_rating(rating_str)
        except ValueError:
            return "", status.HTTP_406_NOT_ACCEPTABLE
    elif available:
        if available != "True":
            return "", status.HTTP_406_NOT_ACCEPTABLE
        products = Product.find_by_availability()
        results = [product.serialize() for product in products]
    else:
        products = Product.all()
        results = [product.serialize() for product in products]
    app.logger.info("Returning %d products", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# RETRIEVE A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["GET"])
def get_products(product_id):
    """
    Retrieve a single Product

    This endpoint will return a Product based on it's id
    """
    app.logger.info("Request for product with id: %s", product_id)
    product = Product.find(product_id)
    if not product:
        abort(
            status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found."
        )

    app.logger.info("Returning product: %s", product.name)
    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# ADD A NEW PRODUCT
######################################################################
@app.route("/products", methods=["POST"])
def create_products():
    """
    Creates a Product
    This endpoint will create a Product based the data in the body that is posted
    """
    app.logger.info("Request to create a product")
    check_content_type("application/json")
    product = Product()
    product.deserialize(request.get_json())
    app.logger.info("Here Deserialization done")
    product.create()
    message = product.serialize()
    location_url = url_for("get_products", product_id=product.id, _external=True)

    app.logger.info("Product with ID [%s] created.", product.id)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# DELETE A PRODUCT
######################################################################


@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_products(product_id):
    """Delete a Product"""
    app.logger.info("Request to delete product with id: %s", product_id)
    product = Product.find(product_id)
    if product:
        product.delete()

    app.logger.info("Product with ID [%s] delete complete.", product_id)
    return "", status.HTTP_204_NO_CONTENT


######################################################################
# UPDATE AN EXISTING PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_products(product_id):
    """
    Update a Product

    This endpoint will update a Product based the body that is posted
    """
    app.logger.info("Request to update product with id: %s", product_id)
    check_content_type("application/json")

    product = Product.find(product_id)
    if not product:
        abort(
            status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found."
        )

    product.deserialize(request.get_json())
    product.id = product_id
    product.update()

    app.logger.info("Product with ID [%s] updated.", product.id)
    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE THE RATING OF A PRODUCT
######################################################################
@app.route("/products/<int:product_id>/rating", methods=["PUT"])
def update_rating_of_product(product_id):
    """
    Updates the rating of a product on the basis of feedback provided.
    Args:
        product_id (_type_): _description_
    """
    app.logger.info("Request to update the rating of the product with id: %s", product_id)
    check_content_type("application/json")
    product = Product.find(product_id)
    if not product:
        app.logger.info("Inside this condition")
        abort(
            status.HTTP_404_NOT_FOUND, description=f"Product with id '{product_id}' was not found."
        )
    new_rating = request.get_json()
    if not isinstance(new_rating["rating"], int):
        abort(
            status.HTTP_406_NOT_ACCEPTABLE, description="Rating should be of integer datatype"
        )
    if new_rating["rating"] <= 0 or new_rating["rating"] > 5:
        abort(
            status.HTTP_406_NOT_ACCEPTABLE, description="The ratings can be from [1,5]"
        )
    if new_rating["rating"] is not None:
        product.id = product_id
        myJson = product.serialize()
        product.deserialize(myJson)
        product.id = product_id
        if product.no_of_users_rated is None or product.no_of_users_rated == 0:
            product.no_of_users_rated = 1
        else:
            product.no_of_users_rated = product.no_of_users_rated + 1
        if product.cumulative_ratings is None or product.cumulative_ratings == 0:
            product.cumulative_ratings = new_rating["rating"]
        else:
            product.cumulative_ratings = product.cumulative_ratings + new_rating["rating"]
        product.rating = product.cumulative_ratings / product.no_of_users_rated
        product.update()
        app.logger.info("Product with ID [%s] updated.", product.id)
    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """Initializes the SQLAlchemy app"""
    global app
    Product.init_db(app)


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        "Content-Type must be {}".format(media_type),
    )
# @app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
# def method_not_supported(error):
#     """Handles unsupported HTTP methods with 405_METHOD_NOT_ALLOWED"""
#     return (
#         jsonify(
#             status=status.HTTP_405_METHOD_NOT_ALLOWED,
#             error="Method not Allowed",
#             message=str(error),
#         ),
#         status.HTTP_405_METHOD_NOT_ALLOWED,
#     )
