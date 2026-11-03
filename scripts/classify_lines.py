"""Classify every line image in an OCR-D file group and register JSON results."""

from concurrent.futures import ProcessPoolExecutor, as_completed
import json
from multiprocessing import get_context
from pathlib import Path
import sys

from ocrd import Resolver
from ocrd.workspace import Workspace
from tqdm import tqdm


_classifier = None


def _init_worker():
    import torch
    from ocrd_typegroups_classifier.model_paths import bundled_model_path
    from ocrd_typegroups_classifier.typegroups_classifier import TypegroupsClassifier

    torch.set_num_threads(1)
    global _classifier
    _classifier = TypegroupsClassifier.load(bundled_model_path())


def _classify(image_path):
    from ocrd_typegroups_classifier.cli.classify import classify_image

    return classify_image(_classifier, image_path)


def main(input_group, output_group, jobs):
    if jobs < 1:
        raise SystemExit("JOBS must be at least 1")
    workspace = Workspace(Resolver(), str(Path.cwd()))
    images = [file for file in workspace.mets.find_files(fileGrp=input_group)
              if file.mimetype.startswith("image/")]
    if not images:
        raise SystemExit(f"No images in {input_group}")

    with ProcessPoolExecutor(max_workers=min(jobs, len(images)),
                             mp_context=get_context("spawn"),
                             initializer=_init_worker) as executor:
        futures = {executor.submit(_classify, image.local_filename): image
                   for image in images}
        for future in tqdm(as_completed(futures), total=len(images),
                           desc="Classifying", unit="line"):
            image = futures[future]
            scores = future.result()
            file_id = f"{output_group}_{image.ID}"
            workspace.add_file(
                output_group,
                file_id=file_id,
                page_id=image.pageId,
                mimetype="application/json",
                local_filename=f"{output_group}/{file_id}.json",
                content=json.dumps(scores, indent=2) + "\n",
                force=True,
            )
    workspace.save_mets()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]))
