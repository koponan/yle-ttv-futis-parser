import cProfile
import pstats

from pathlib import Path

def run(rep_text: str):
    from ttv_parser import parser

    prof = cProfile.Profile()
    prof.enable()
    parser.parse_report(rep_text)
    prof.disable()

    stats = pstats.Stats(prof).strip_dirs().sort_stats("cumulative")
    stats.print_stats(20)

if __name__ == "__main__":
    rep_text = Path("test/data/goals_to_goals.txt").read_text("utf-8")
    run(rep_text)
