"""Locations of the model bundled with this package."""

from importlib.resources import files


def bundled_model_path():
    return str(files("ocrd_typegroups_classifier.models").joinpath("classifier.tgc"))
