"""Tests for views.py."""

import pytest

import ckanext.advanced_search.validators as validators


import ckan.plugins.toolkit as tk


@pytest.mark.ckan_config("ckan.plugins", "example_extension")
@pytest.mark.usefixtures("with_plugins")
def test_example_extension_blueprint(app, reset_db):
    resp = app.get(tk.h.url_for("example_extension.page"))
    assert resp.status_code == 200
    assert resp.body == "Hello, example_extension!"
