#!/usr/bin/env python3
import argparse
import csv
import sys
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(
        description="Count each complaint type per borough for a range of creation dates."
    )
    parser.add_argument("-i", "--input", required=True,
                        help="input 311 CSV file")
    parser.add_argument("-s", "--start", required=True,
                        help="start date, inclusive (YYYY-MM-DD)")
    parser.add_argument("-e", "--end", required=True,
                        help="end date, inclusive (YYYY-MM-DD)")
    parser.add_argument("-o", "--output",
                        help="output CSV file (default: print to stdout)")
    return parser.parse_args()


def main():
    args = parse_args()
    print(args)


if __name__ == "__main__":
    main()

