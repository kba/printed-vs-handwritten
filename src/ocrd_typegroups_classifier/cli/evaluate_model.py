from pathlib import Path
import torch
from torchvision.datasets import ImageFolder
from tqdm import tqdm

from ocrd_typegroups_classifier.typegroups_classifier import TypegroupsClassifier
from ocrd_typegroups_classifier.model_paths import bundled_model_path


def main():
    model_path = Path('models/classifier.tgc')

    tgc = TypegroupsClassifier.load(str(model_path) if model_path.exists() else bundled_model_path())

    validation = ImageFolder('lines/validation', transform=None)
    validation.target_transform = tgc.classMap.get_target_transform(validation.class_to_idx)
    good = 0
    bad  = 0
    with torch.no_grad():
        tgc.network.eval()
        for idx in tqdm(range(validation.__len__()), desc='Evaluation'):
            sample, target = validation.__getitem__(idx)
            path, _ = validation.samples[idx]
            if target==-1:
                continue
            result = tgc.classify(sample, 224, 64, True)
            highscore = max(result)
            label = tgc.classMap.cl2id[result[highscore]]
            if target==label:
                good += 1
            else:
                bad += 1

    accuracy = 100*good/float(good+bad)

    print('    Good:', good)
    print('     Bad:', bad)
    print('Accuracy:', accuracy)


if __name__ == "__main__":
    main()
