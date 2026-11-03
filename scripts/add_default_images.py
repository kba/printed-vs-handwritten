"""Add DEFAULT images to the current OCR-D workspace in one METS update."""

from pathlib import Path
import re

from ocrd import Resolver
from ocrd.workspace import Workspace
from ocrd_utils import EXT_TO_MIME


def main():
    root = Path.cwd()
    workspace = Workspace(Resolver(), str(root))
    if "DEFAULT" in workspace.mets.file_groups:
        return

    for image in sorted((root / "DEFAULT").iterdir()):
        mime_type = EXT_TO_MIME.get(image.suffix.lower())
        if not image.is_file() or not mime_type or not mime_type.startswith("image/"):
            continue
        number = "".join(re.findall(r"\d", image.stem)[-4:])
        workspace.add_file(
            "DEFAULT",
            file_id=f"FILE_{number}_DEFAULT",
            page_id=f"PHYS_{number}",
            mimetype=mime_type,
            local_filename=image.relative_to(root).as_posix(),
        )
    workspace.save_mets()


if __name__ == "__main__":
    main()
