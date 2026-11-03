"""Command line classification of a single text line image."""

import argparse
import json
from math import exp

from PIL import Image

from ocrd_typegroups_classifier.model_paths import bundled_model_path
from ocrd_typegroups_classifier.typegroups_classifier import TypegroupsClassifier


def main(argv=None):
    parser = argparse.ArgumentParser(description="Classify a text line as printed or handwritten")
    parser.add_argument("image", help="image to classify")
    parser.add_argument("--model", default=bundled_model_path(), help="classifier model file")
    args = parser.parse_args(argv)

    with Image.open(args.image) as img:
        classifier = TypegroupsClassifier.load(args.model)
        background = Image.new("RGBA", img.size, "white")
        rgb_image = Image.alpha_composite(background, img.convert("RGBA")).convert("RGB")
        result = classifier.classify(rgb_image, 75, 64, False)

    total = sum(exp(score) for score in result.values())
    print(json.dumps({label: exp(score) / total for label, score in result.items()}))


if __name__ == "__main__":
    main()
