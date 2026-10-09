#!/usr/bin/env python3
import argparse
import csv
from datetime import datetime

TIME_FORMAT = "%m/%d/%Y %I:%M:%S %p"
# The dataset was exported on 2025-09-28, so later closed dates are data-entry errors.
EXPORT_CUTOFF = datetime(2025, 9, 29)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compute the monthly average 311 response time (hours) per zipcode and overall."
    )
    parser.add_argument("-i", "--input", required=True, help="trimmed 2024 311 CSV file")
    parser.add_argument("-o", "--output", required=True, help="output CSV of monthly averages")
    return parser.parse_args()


def clean_zip(raw):
    zipcode = (raw or "").strip()[:5]
    if len(zipcode) != 5 or not zipcode.isdigit() or zipcode == "00000":
        return None
    return zipcode


def main():
    args = parse_args()
    totals = {}
    kept = skipped = 0
    with open(args.input, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            zipcode = clean_zip(row["Incident Zip"])
            if zipcode is None or not row["Closed Date"]:
                skipped += 1
                continue
            try:
                created = datetime.strptime(row["Created Date"], TIME_FORMAT)
                closed = datetime.strptime(row["Closed Date"], TIME_FORMAT)
            except (ValueError, TypeError):
                skipped += 1
                continue
            hours = (closed - created).total_seconds() / 3600
            if hours < 0 or closed >= EXPORT_CUTOFF:
                skipped += 1
                continue
            month = closed.strftime("%Y-%m")
            for key in ((zipcode, month), ("ALL", month)):
                entry = totals.setdefault(key, [0.0, 0])
                entry[0] += hours
                entry[1] += 1
            kept += 1

    with open(args.output, "w", newline="", encoding="utf-8") as out:
        writer = csv.writer(out)
        writer.writerow(["zipcode", "month", "avg_hours", "count"])
        for (zipcode, month), (total, count) in sorted(totals.items()):
            writer.writerow([zipcode, month, round(total / count, 3), count])

    print(f"kept {kept:,} incidents, skipped {skipped:,}; wrote {len(totals):,} rows to {args.output}")


if __name__ == "__main__":
    main()
