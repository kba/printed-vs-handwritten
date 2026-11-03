import argparse
import sys
from math import exp
from PIL import Image
from ocrd_typegroups_classifier.typegroups_classifier import TypegroupsClassifier
from ocrd_typegroups_classifier.model_paths import bundled_model_path


parser = argparse.ArgumentParser(description="Classify a text line as printed or handwritten")
parser.add_argument("image", help="image to classify")
parser.add_argument("--model", default=bundled_model_path(), help="classifier model file")
args = parser.parse_args()

img = Image.open(args.image)
tgc = TypegroupsClassifier.load(args.model)

result = tgc.classify(img, 75, 64, False)
esum = 0
for key in result:
    esum += exp(result[key])
for key in result:
    result[key] = exp(result[key]) / esum
print(result)
