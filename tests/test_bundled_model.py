"""Smoke test for loading the legacy pickled checkpoint with current Torch."""

from math import isfinite

from PIL import Image

from ocrd_typegroups_classifier.model_paths import bundled_model_path
from ocrd_typegroups_classifier.typegroups_classifier import TypegroupsClassifier


def test_bundled_model_classifies_image():
    classifier = TypegroupsClassifier.load(bundled_model_path())
    scores = classifier.classify(Image.new("RGB", (32, 32), "white"), stride=32, batch_size=1)

    assert set(scores) == {"handwritten", "printed"}
    assert all(isfinite(score) for score in scores.values())
