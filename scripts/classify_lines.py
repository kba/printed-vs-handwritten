"""Classify every line image in an OCR-D file group and register JSON results."""

import json
from pathlib import Path
import subprocess
import sys

from ocrd import Resolver
from ocrd.workspace import Workspace
from tqdm import tqdm


def main(input_group, output_group):
    workspace = Workspace(Resolver(), str(Path.cwd()))
    images = [file for file in workspace.mets.find_files(fileGrp=input_group)
              if file.mimetype.startswith("image/")]
    if not images:
        raise SystemExit(f"No images in {input_group}")

    for image in tqdm(images, desc="Classifying", unit="line"):
        result = subprocess.check_output(
            ["printed-vs-handwritten", image.local_filename], text=True
        )
        scores = json.loads(result)
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
    main(*sys.argv[1:])
