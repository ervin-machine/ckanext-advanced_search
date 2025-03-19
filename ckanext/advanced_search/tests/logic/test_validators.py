"""Tests for validators.py."""

import pytest

import ckan.plugins.toolkit as tk

from ckanext.advanced_search.logic import validators


def test_example_extension_reauired_with_valid_value():
    assert validators.example_extension_required("value") == "value"


def test_example_extension_reauired_with_invalid_value():
    with pytest.raises(tk.Invalid):
        validators.example_extension_required(None)
