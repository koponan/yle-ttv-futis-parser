from dataclasses import dataclass
import time
from typing import List, Optional

@dataclass
class Event:
    time: int
    player: str
    team: str

@dataclass
class Goal(Event):
    type: str

@dataclass
class RedCard(Event):
    pass

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
    subpage_count: int
    head: str
    body: List[Match]

    def __str__(self) -> str:
        ret = f"Subpages: {self.subpage_count}\n"
        ret += self.head + "\n"
        ret += "----------------\n"
        for match in self.body:
            ret += str(match) + "\n"

        return ret.rstrip("\n")