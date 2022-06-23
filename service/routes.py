"""
My Service

Describe what your service does here
"""

# import os
# import sys
# import logging
from flask import url_for, jsonify
# from flask import Flask, request, make_response, abort
from .utils import status  # HTTP Status Codes
from service.models import YourResourceModel

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        # "Reminder: return some useful information in json format about the service here",
        jsonify(name="Product REST API Service", paths=url_for("index", _external=True),
                version="1.0"),
        status.HTTP_200_OK,
    )


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """ Initializes the SQLAlchemy app """
    global app
    YourResourceModel.init_db(app)
