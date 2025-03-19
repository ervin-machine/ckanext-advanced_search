import ckan.plugins.toolkit as tk


def example_extension_required(value):
    if not value or value is tk.missing:
        raise tk.Invalid(tk._("Required"))
    return value


def get_validators():
    return {
        "example_extension_required": example_extension_required,
    }
