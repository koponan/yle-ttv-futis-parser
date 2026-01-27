import argparse
import linecache
import sys
import traceback
import tracemalloc
from pathlib import Path
from typing import List, Union

from ttv_parser import parser

def main(args: argparse.Namespace):
    try:
        rep_text = Path(args.report).read_text("utf-8")
    except Exception as e:
        print(f"Failed to read file (path={args.report})", file=sys.stderr)
        print(traceback.print_exc(), file=sys.stderr)
        exit(1)

    tracemalloc.start()
    parsed = parser.parse_report(rep_text)
    snapshot = tracemalloc.take_snapshot()

    if args.o is not None:
        snapshot.dump(args.o)
        return

    if args.compare is not None:
        old = tracemalloc.Snapshot.load(args.compare)
        report_comparison(snapshot, old)
        return

    report_single(snapshot)

def report_single(snapshot: tracemalloc.Snapshot):
    snapshot = filter_snapshot(snapshot)
    stats = snapshot.statistics("traceback")
    limit = 10

    print(fmt_total(snapshot))
    print(f"Top {limit}:")

    for stat in stats[:limit]:
        print(f"{fmt_file_and_line(stat)} Size={fmt_size(stat.size)} Blocks={stat.count}\n\t{fmt_trace(stat)}")

def report_comparison(new: tracemalloc.Snapshot, old: tracemalloc.Snapshot):
    new = filter_snapshot(new)
    old = filter_snapshot(old)
    stats: List[tracemalloc.StatisticDiff] = new.compare_to(old, "traceback")
    limit = 10

    print(fmt_total(new, old))
    print(f"Top {limit}:")

    for stat in stats[:limit]:
        print(f"{fmt_file_and_line(stat)} Size={fmt_size(stat.size)} ({fmt_size(stat.size_diff)}) Blocks={stat.count}\n\t{fmt_trace(stat)}")

def filter_snapshot(snapshot: tracemalloc.Snapshot):
    return snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap*"),
        tracemalloc.Filter(False, "/Library/Developer/*"),
        tracemalloc.Filter(False, "<unknown>"),
    ))

def fmt_total(snapshot: tracemalloc.Snapshot, other: Union[None, tracemalloc.Snapshot] = None):
    size_total = sum(stat.size for stat in snapshot.statistics("traceback"))
    if other is None:
        return f"Snapshot total {fmt_size(size_total, 2)}"

    size_other = sum(stat.size for stat in other.statistics("traceback"))
    size_diff = size_total - size_other
    return f"Snapshot total {fmt_size(size_total, 2)} ({fmt_size(size_diff, 2)})"

def fmt_file_and_line(stat: tracemalloc.Statistic):
    frame = stat.traceback[0]
    repo_prefix = "yle-ttv-futis-parser/"
    fname = frame.filename.split(repo_prefix)[1] if repo_prefix in frame.filename else frame.filename
    return f"{fname}:{frame.lineno}"

def fmt_trace(stat: tracemalloc.Statistic):
    frame = stat.traceback[0]
    return linecache.getline(frame.filename, frame.lineno).strip()

def fmt_size(size: int, decimals=1):
    return f"{(size / 1024):.{decimals}f} KiB"

def args():
    p = argparse.ArgumentParser()
    p.add_argument(
        "report",
        type=str,
        help="File to parse."
    )

    conflicting_flags = p.add_mutually_exclusive_group()
    conflicting_flags.add_argument(
        "-o", "--output",
        type=str,
        help="File to save binary snapshot. When provided, standard output is omitted."
    )
    conflicting_flags.add_argument(
        "--compare",
        type=str,
        help="Snapshot file to which results are compared."
    )

    return p.parse_args()

if __name__ == "__main__":
    main(args())
