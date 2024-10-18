import unittest

from datetime import date
from dataclasses import dataclass
from typing import List

from ttv_parser import parser
from ttv_parser.models import Match, Goal, Report, RedCard, EventTime, ReportHead

def load_text(fname: str):
    with open(f"test/data/{fname}", "r") as f:
        return f.read()

@dataclass
class TestReport:
    raw: str
    expected: Report

COMPETITION = "ENGLANNIN VAR-LIIGA"
DATE = date.today().replace(month=1, day=22)
SUBPAGES = [1, 1]

class ParserTest(unittest.TestCase):
    def assertReportsEqual(self, actual: Report, expected: Report):
        self.assertEqual(actual.head, expected.head)
        self.assertMatchesEqual(actual, expected)

    def assertMatchesEqual(self, actual: Report, expected: Report):
        self.assertListEqual(actual.body, expected.body)

    def getReportHead(self, comp: str = COMPETITION, date: date = DATE, subpages: List[int] = SUBPAGES):
        return ReportHead(comp, date, subpages)

    def setUp(self) -> None:
        self.goalless_draw = TestReport(None, None)
        self.goalless_draw.raw = load_text("goalless_draw.txt")
        self.goalless_draw.expected = Report(
            self.getReportHead(),
            [
                Match(
                    "Null City",
                    "Bazpool",
                    None,
                    [0, 0],
                    [0, 0],
                    []
                )
            ]
        )

        self.goal_to_nil = TestReport(None, None)
        self.goal_to_nil.raw = load_text("goal_to_nil.txt")
        self.goal_to_nil.expected = Report(
            self.getReportHead(),
            [
                Match(
                    "Barham",
                    "Foo Utd",
                    None,
                    [0, 0],
                    [0, 1],
                    [
                        Goal(89, "McDominate", "Visitor", "m"),
                    ]
                )
            ]
        )

        self.goals_to_goals = TestReport(None, None)
        self.goals_to_goals.raw = load_text("goals_to_goals.txt")
        self.goals_to_goals.expected = Report(
            self.getReportHead(),
            [
                Match(
                    "Null City",
                    "Foo Utd",
                    None,
                    [0, 2],
                    [1, 2],
                    [
                        Goal(30, "Barnacho", "Visitor", "m"),
                        Goal(39, "Mainoom", "Visitor", "m"),
                        Goal(87, "Doc", "Host", "m")
                    ]
                )
            ]
        )

        self.many_matches = TestReport(None, None)
        self.many_matches.raw = load_text("many_matches.txt")
        self.many_matches.expected = Report(
            self.getReportHead(),
            [
                Match(
                    "Barham",
                    "Foo Utd",
                    None,
                    [0, 0],
                    [0, 1],
                    [
                        Goal(89, "McDominate", "Visitor", "m")
                    ]
                ),
                Match(
                    "Bazpool",
                    "Null City",
                    None,
                    [0, 1],
                    [1, 1],
                    [
                        Goal(23, "Halland", "Visitor", "m"),
                        Goal(50, "Nanez", "Host", "m")
                    ]
                )
            ]
        )

        self.own_goal = TestReport(None, None)
        self.own_goal.raw = load_text("own_goal.txt")
        self.own_goal.expected = Report(
            self.getReportHead(),
            [
                Match(
                    "Foo Utd",
                    "Barham",
                    None,
                    [1, 1],
                    [3, 2],
                    [
                        Goal(10, "Pom", "Visitor", "m"),
                        Goal(45, "Ramero", "Host", "om"),
                        Goal(48, "Pom", "Visitor", "m"),
                        Goal(78, "McDominate", "Host", "m"),
                        Goal(90, "Mainoom", "Host", "m")
                    ]
                )
            ]
        )

        self.penalty = TestReport(None, None)
        self.penalty.raw = load_text("penalty.txt")
        self.penalty.expected = Report(
            self.getReportHead(),
            [
                Match(
                    "Foo Utd",
                    "Bazpool",
                    None,
                    [1, 0],
                    [2, 1],
                    [
                        Goal(10, "Barnacho", "Host", "m"),
                        Goal(50, "Mac Tester", "Visitor", "rp"),
                        Goal(90, "McDominate", "Host", "m")
                    ]
                )
            ]
        )

        self.red_card = TestReport(None, None)
        self.red_card.raw = load_text("red_card.txt")
        self.red_card.expected = Report(
            self.getReportHead(),
            [
                Match(
                    "Bazpool",
                    "Foo Utd",
                    None,
                    [1, 0],
                    [1, 1],
                    [
                        Goal(30, "Nanez", "Host", "m"),
                        Goal(75, "McDominate", "Visitor", "m"),
                        RedCard(80, "Nanez", "Host")
                    ]
                )
            ]
        )

        self.multi_digit_goals = TestReport(None, None)
        self.multi_digit_goals.raw = load_text("multi_digit_goals.txt")
        self.multi_digit_goals.expected = Report(
            self.getReportHead(),
            [
                Match(
                    "Unlikely",
                    "Many Goals",
                    None,
                    [10, 5],
                    [12, 9],
                    []
                )
            ]
        )

        self.ongoing_match = TestReport(None, None)
        self.ongoing_match.raw = load_text("ongoing_match.txt")
        self.ongoing_match.expected = Report(
            self.getReportHead(),
            [
                Match(
                    "Bazpool",
                    "Foo Utd",
                    None,
                    [1, 0],
                    None,
                    [
                        Goal(30, "Nanez", "Host", "m")
                    ]
                )
            ]
        )

        self.upcoming_matches = TestReport(None, None)
        self.upcoming_matches.raw = load_text("upcoming_matches.txt")

        self.added_time = TestReport(
            load_text("added_time.txt"),
            Report(
                self.getReportHead(),
                [
                    Match(
                        "Bazpool",
                        "Barham",
                        None,
                        [1, 0],
                        [2, 0],
                        [
                            Goal(40, "Nanez", "Host", "m"),
                            Goal(EventTime(90, 2), "Mac Tester", "Host", "m")
                        ]
                    )
                ]
            )
        )

    def test_1_goalless_draw(self):
        res = parser.parse_report(self.goalless_draw.raw)
        self.assertReportsEqual(res, self.goalless_draw.expected)

    def test_2_goal_to_nil(self):
        res = parser.parse_report(self.goal_to_nil.raw)
        self.assertReportsEqual(res, self.goal_to_nil.expected)

    def test_3_goals_to_goals(self):
        res = parser.parse_report(self.goals_to_goals.raw)
        self.assertReportsEqual(res, self.goals_to_goals.expected)

    def test_4_many_matches(self):
        res = parser.parse_report(self.many_matches.raw)
        self.assertReportsEqual(res, self.many_matches.expected)

    def test_5_own_goal(self):
        res = parser.parse_report(self.own_goal.raw)
        self.assertReportsEqual(res, self.own_goal.expected)

    def test_6_penalty(self):
        res = parser.parse_report(self.penalty.raw)
        self.assertReportsEqual(res, self.penalty.expected)

    def test_7_red_card(self):
        res = parser.parse_report(self.red_card.raw)
        self.assertReportsEqual(res, self.red_card.expected)

    def test_8_multi_digit_goals(self):
        res = parser.parse_report(self.multi_digit_goals.raw)
        self.assertReportsEqual(res, self.multi_digit_goals.expected)

    def test_9_ongoing_match(self):
        res = parser.parse_report(self.ongoing_match.raw)
        self.assertReportsEqual(res, self.ongoing_match.expected)

    def test_10_upcoming_matches(self):
        res = parser.parse_report(self.upcoming_matches.raw)
        first, second = res.body
        self.assertListEqual(
            [first.kickoff.tm_hour, first.kickoff.tm_min],
            [16, 0]
        )
        self.assertListEqual(
            [second.kickoff.tm_hour, second.kickoff.tm_min],
            [18, 30]
        )

    def test_11_added_time(self):
        res = parser.parse_report(self.added_time.raw)
        self.assertReportsEqual(res, self.added_time.expected)

    def test_12_report_head(self):
        head_with_arbitrary_spacing = "   ITALIAN   SERIE  Ä     01.05.    1/2 "
        rep = self.goalless_draw.raw
        rep_parts = rep.split("\n", maxsplit=1)
        rep = "\n".join([head_with_arbitrary_spacing, rep_parts[1]])
        res = parser.parse_report(rep)
        self.assertEqual(
            res.head,
            ReportHead(
                "ITALIAN SERIE Ä",
                date.today().replace(month=5, day=1),
                [1, 2]
            )
        )

if __name__ == "__main__":
    unittest.main(verbosity=2)
