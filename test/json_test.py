import json
import unittest

from ttv_parser.models import *

PLAYER = "Owen Goal"
TEAM = "Stonks FC"

class JsonTest(unittest.TestCase):
    def test_1_events(self):
        goal = Goal(1, PLAYER, TEAM, "m")
        self.assert_event(goal, EventType.GOAL)

        own_goal = Goal(2, PLAYER, TEAM, "om")
        self.assert_event(own_goal, EventType.OWN_GOAL)

        pen = Goal(3, PLAYER, TEAM, "rp")
        self.assert_event(pen, EventType.PENALTY)

        pen_miss = MissedPenalty(4, PLAYER, TEAM)
        self.assert_event(pen_miss, EventType.MISSED_PENALTY)

        red = RedCard(5, PLAYER, TEAM)
        self.assert_event(red, EventType.RED_CARD)

    def test_2_serialize_event(self):
        goal = Goal(1, "PP", "TT", "m")
        actual_str = json.dumps(goal.json_value(), ensure_ascii=False)
        self.assertEqual(
            actual_str,
            '{"event_type": "GOAL", "time": {"regular": 1, "added": null}, "player": "PP", "team": "TT", "type": "m"}'
        )

    def assert_event(self, event: Event, expected_type: EventType):
        expected = {
            "event_type": expected_type.value,
            "time": {
                "regular": event.time.regular,
                "added": event.time.added
            },
            "player": event.player,
            "team": event.team
        }
        if isinstance(event, Goal):
            expected["type"] = event.type

        self.assertDictEqual(
            event.json_value(),
            expected
        )

if __name__ == "__main__":
    unittest.main(verbosity=2)
