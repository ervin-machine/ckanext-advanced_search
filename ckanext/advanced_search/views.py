from flask import Blueprint


example_extension = Blueprint(
    "example_extension", __name__)


def page():
    return "Hello, example_extension!"


example_extension.add_url_rule(
    "/example_extension/page", view_func=page)


def get_blueprints():
    return [example_extension]
