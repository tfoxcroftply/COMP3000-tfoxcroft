from flask import Blueprint

testBlueprint = Blueprint("test", __name__)

@testBlueprint.route("/")
def test():
    return "Test"