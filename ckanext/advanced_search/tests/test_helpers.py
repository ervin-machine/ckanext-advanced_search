"""Tests for helpers.py."""

import ckanext.advanced_search.helpers as helpers


def test_example_extension_hello():
    assert helpers.example_extension_hello() == "Hello, example_extension!"
