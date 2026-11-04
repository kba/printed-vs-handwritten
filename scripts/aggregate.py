"""Summarize line classification scores for each PPN workspace."""

import argparse
import csv
import json
from pathlib import Path
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


def main(ppns, file_group, ground_truth_path, threshold, output):
    if not 0 <= threshold <= 1:
        raise SystemExit("THRESHOLD must be between 0 and 1")
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
        gt = ground_truth.get(workspace.name, "?")
        if gt in ("handwritten", "printed"):
            mean = fmean(handwritten if gt == "handwritten" else printed)
            gt = ("✅ " if mean > threshold else "❌ ") + gt
        rows.append((workspace.name, gt,
                     str(len(files)), *summarize(handwritten),
                     *summarize(printed)))

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
    args = parser.parse_args()
    main(args.ppns, args.file_group, args.ground_truth, args.threshold, args.output)
