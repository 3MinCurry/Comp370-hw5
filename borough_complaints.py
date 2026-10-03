#!/usr/bin/env python3
import argparse
import csv
import sys
from datetime import datetime

CREATED_FORMAT = "%m/%d/%Y %I:%M:%S %p"


def date_arg(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid date '{value}', expected YYYY-MM-DD")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Count each complaint type per borough for a range of creation dates."
    )
    parser.add_argument("-i", "--input", required=True,
                        help="input 311 CSV file")
    parser.add_argument("-s", "--start", required=True, type=date_arg,
                        help="start date, inclusive (YYYY-MM-DD)")
    parser.add_argument("-e", "--end", required=True, type=date_arg,
                        help="end date, inclusive (YYYY-MM-DD)")
    parser.add_argument("-o", "--output",
                        help="output CSV file (default: print to stdout)")
    args = parser.parse_args()
    if args.start > args.end:
        parser.error("start date must be on or before end date")
    return args


def count_complaints(input_path, start, end):
    counts = {}
    with open(input_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                created = datetime.strptime(row["Created Date"], CREATED_FORMAT).date()
            except (ValueError, TypeError):
                continue
            if created < start or created > end:
                continue
            key = (row["Complaint Type"], row["Borough"])
            counts[key] = counts.get(key, 0) + 1
    return counts


def write_counts(counts, out):
    writer = csv.writer(out)
    writer.writerow(["complaint type", "borough", "count"])
    for (complaint_type, borough), count in sorted(counts.items()):
        writer.writerow([complaint_type, borough, count])


def main():
    args = parse_args()
    counts = count_complaints(args.input, args.start, args.end)
    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as out:
            write_counts(counts, out)
    else:
        write_counts(counts, sys.stdout)


if __name__ == "__main__":
    main()
