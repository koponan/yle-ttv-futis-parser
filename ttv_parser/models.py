from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from functools import total_ordering
import time
from typing import List, Optional

@dataclass
class Event:
    time: EventTime
    player: str
    team: str

    def __init__(self, time: int | EventTime, player: str, team: str):
        self.time = time if isinstance(time, EventTime) else EventTime(time, None)
        self.player = player
        self.team = team

@total_ordering
@dataclass
class EventTime:
    regular: int
    added: int | None

    def __str__(self):
        return f"{self.regular}+{self.added}" if self.added else str(self.regular)

    def __repr__(self):
        return str(self)

    def __lt__(self, other: EventTime):
        """
        40 < 45
        45 < 45+2
        45+2 < 46
        """
        if self.regular == other.regular:
            self_total = self.regular + self.added if self.added else 0
            other_total = other.regular + other.added if other.added else 0
            return self_total < other_total

        return self.regular < other.regular

@dataclass
class Goal(Event):
    type: str

    def __init__(self, time: int | EventTime, player: str, team: str, type: str):
        super().__init__(time, player, team)
        self.type = type

@dataclass
class RedCard(Event):
    def __init__(self, time: int | EventTime, player: str, team: str):
        super().__init__(time, player, team)

@dataclass
class Match:
    host: str
    visitor: str
    kickoff: time.struct_time
    ht_score: List[int]
    ft_score: List[int]
    events: List[Event]

    def __str__(self) -> str:
        ret = f"{self.host} vs {self.visitor} {self.score_str(self.ft_score)} ({self.score_str(self.ht_score)}) {'{'}\n"
        for ev in self.events:
            ret += f"    {ev}\n"

        ret += "}"
        return ret

    def score_str(self, score: Optional[List[int]]):
        if score is None:
            return ""
        return '-'.join(map(lambda n: str(n), score))

@dataclass
class Report:
    head: ReportHead
    body: List[Match]

    def __str__(self) -> str:
        ret = str(self.head) + "\n"
        ret += "----------------\n"
        for match in self.body:
            ret += str(match) + "\n"

        return ret.rstrip("\n")

@dataclass
class ReportHead:
    competition: str
    date: date
    subpages: List[int]
