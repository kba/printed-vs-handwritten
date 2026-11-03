"""
OCR-D conformant command line interface
"""
import argparse

from PIL import Image

from ..typegroups_classifier import TypegroupsClassifier


def cli(argv=None):
    """Classify an image using an explicitly supplied model file."""
    parser = argparse.ArgumentParser(description="Classify an image with a model file")
    parser.add_argument("network_file")
    parser.add_argument("image_file")
    parser.add_argument("stride", nargs="?", type=int, default=96)
    args = parser.parse_args(argv)
    classifier = TypegroupsClassifier.load(args.network_file)
    with Image.open(args.image_file) as image:
        print(classifier.run(image, args.stride))


if __name__ == "__main__":
    cli()
