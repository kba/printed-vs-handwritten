"""Summarize line classification scores for each PPN workspace."""

import json
from pathlib import Path
from statistics import fmean, median, pstdev
import sys


def summarize(values):
    return (f"{fmean(values):.4f}", f"{median(values):.4f}",
            f"{pstdev(values):.4f}")


def main(ppns, file_group, ground_truth_path):
    ground_truth = json.loads(Path(ground_truth_path).read_text())
    headers = ("PPN", "GT", "Lines", "H mean", "H median", "H stddev",
               "P mean", "P median", "P stddev")
    rows = []
    for workspace in sorted(Path(ppns).glob("PPN*")):
        if not workspace.is_dir():
            continue
        files = sorted((workspace / file_group).glob("*.json"))
        if not files:
            continue
        scores = [json.loads(path.read_text()) for path in files]
        handwritten = [score["handwritten"] for score in scores]
        printed = [score["printed"] for score in scores]
        rows.append((workspace.name, ground_truth.get(workspace.name, "?"),
                     str(len(files)), *summarize(handwritten),
                     *summarize(printed)))

    if not rows:
        raise SystemExit(f"No classification JSON files found in {ppns}/PPN*/{file_group}")

    widths = [max(len(str(value)) for value in column)
              for column in zip(headers, *rows)]
    print(" | ".join(header.ljust(width) for header, width in zip(headers, widths)))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(" | ".join(value.ljust(width) for value, width in zip(row, widths)))


if __name__ == "__main__":
    main(*sys.argv[1:])
