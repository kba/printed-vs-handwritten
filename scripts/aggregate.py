"""Summarize line classification scores for each PPN workspace."""

import argparse
from collections import defaultdict
import csv
import json
from pathlib import Path
import re
from statistics import fmean, median, pstdev
import sys
from unicodedata import east_asian_width


def summarize(values):
    return (f"{fmean(values):.4f}", f"{median(values):.4f}",
            f"{pstdev(values):.4f}")


def display_width(value):
    return sum(2 if east_asian_width(char) in ("W", "F") else 1 for char in value)


def pad(value, width):
    return value + " " * (width - display_width(value))


def print_markdown(headers, rows):
    widths = [max(display_width(value) for value in column)
              for column in zip(headers, *rows)]

    def print_row(row):
        print("| " + " | ".join(pad(value, width) for value, width in zip(row, widths)) + " |")

    print_row(headers)
    print("| " + " | ".join("-" * width for width in widths) + " |")
    for row in rows:
        print_row(row)


def summary_row(ppn, page, scores, ground_truth, threshold):
    handwritten = [score["handwritten"] for score in scores]
    printed = [score["printed"] for score in scores]
    gt = ground_truth.get(ppn, "?")
    if gt in ("handwritten", "printed"):
        mean = fmean(handwritten if gt == "handwritten" else printed)
        gt = ("✅ " if mean > threshold else "❌ ") + gt
    return (ppn, *((page,) if page is not None else ()), gt, str(len(scores)),
            *summarize(handwritten), *summarize(printed))


def page_from_filename(path):
    match = re.search(r"(?:^|_)(\d{4})(?=_|$)", path.stem)
    if not match:
        raise ValueError(f"Cannot find four-digit page number in {path}")
    return f"PHYS_{match.group(1)}"


def page_scores(workspace_path, file_group):
    by_page = defaultdict(list)
    for path in sorted((workspace_path / file_group).glob("*.json")):
        by_page[page_from_filename(path)].append(json.loads(path.read_text()))
    return by_page


def main(ppns, file_group, ground_truth_path, threshold, output, level):
    if not 0 <= threshold <= 1:
        raise SystemExit("THRESHOLD must be between 0 and 1")
    ground_truth = json.loads(Path(ground_truth_path).read_text())
    headers = (("PPN", "page") if level == "page" else ("PPN",)) + (
        "GT", "Lines", "H mean", "H median", "H stddev",
        "P mean", "P median", "P stddev")
    rows = []
    for workspace in sorted(Path(ppns).glob("PPN*")):
        if not workspace.is_dir():
            continue
        if level == "page":
            for page, scores in sorted(page_scores(workspace, file_group).items()):
                rows.append(summary_row(workspace.name, page, scores,
                                        ground_truth, threshold))
        else:
            files = sorted((workspace / file_group).glob("*.json"))
            if files:
                scores = [json.loads(path.read_text()) for path in files]
                rows.append(summary_row(workspace.name, None, scores,
                                        ground_truth, threshold))

    if not rows:
        raise SystemExit(f"No classification JSON files found in {ppns}/PPN*/{file_group}")

    if output == "markdown":
        print_markdown(headers, rows)
    else:
        writer = csv.writer(sys.stdout, lineterminator="\n")
        writer.writerow(headers)
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ppns", help="directory containing PPN workspaces")
    parser.add_argument("file_group", help="classification result file group")
    parser.add_argument("ground_truth", help="ground truth JSON file")
    parser.add_argument("threshold", type=float, help="minimum mean score for a correct classification")
    parser.add_argument("--output", choices=("csv", "markdown"), default="csv")
    parser.add_argument("--level", choices=("ppn", "page"), default="ppn")
    args = parser.parse_args()
    main(args.ppns, args.file_group, args.ground_truth, args.threshold,
         args.output, args.level)
