from typing import List

from ttv_parser.models import Event, Goal, Match, RedCard, Report

def parse_report(report: str) -> Report:
    report = report.lstrip() # Only left strip to save trailing newlines to signal end of last match
    head, body_raw = report.split("\n", maxsplit=1)
    res = Report(
        get_subpage_count(report),
        head,
        parse_body(body_raw)
    )
    return res

def parse_body(body: str):
    matches = []
    rows = body.split("\n")
    curr_match = None
    for row in rows:
        if isblank(row) and curr_match is not None and curr_match.host is not None:
            # Could also account for end of body
            # to remove need to keep trailing new lines around
            curr_match.events.sort(key=lambda e: e.time)
            matches.append(curr_match)
            curr_match = Match(None, None, [], [], [])
        elif isblank(row):
            curr_match = Match(None, None, [], [], [])
        elif curr_match.host is None:
            curr_match = parse_match_head(row.strip())
        else:
            # parse event rows in reverse to reduce ambiguity in row structure
            curr_match.events += parse_match_event_row_reverse(row)

    return matches

def isblank(str: str):
    return not str or str.isspace()

def parse_match_head(head: str):
    head = head.strip()
    home_team = []
    visitor_team = []
    scoreline = []
    item_to_build = home_team
    collected_character_index = None

    for i, c in enumerate(head):
        # check which item underway since scoreline also has '-'
        if c == "-" and item_to_build is home_team:
            item_to_build = visitor_team
        elif c.isspace():
            pass
        # Since clubs may have numbers in name e.g. 'Mainz 05'
        # look for '-' after number to identify scoreline
        elif at_number_followed_by_dash(head, i):
            scoreline = parse_score(head[i:])
            break
        elif collected_character_index == i - 2 and (item_to_build is home_team or item_to_build is visitor_team):
            item_to_build.append(" ")
            item_to_build.append(c)
            collected_character_index = i
        else:
            item_to_build.append(c)
            collected_character_index = i

    return Match(
        list_to_str(home_team),
        list_to_str(visitor_team),
        scoreline[2:4],
        scoreline[:2],
        []
    )

def parse_match_event_row_reverse(row: str):
    events: List[Event] = []
    event = None
    player = ""
    time = ""
    first_team = "Visitor"
    last_team = "Host"
    building_player = False
    building_time = False
    building_time_prefix = False
    on_right_margin = True
    space_within_player = False

    for c in reversed(row):
        if c.isspace() and on_right_margin:
            continue
        elif c.isdigit():
            on_right_margin = False
            if building_player:
                building_player = False
                space_within_player = False
                event.player = player
                player = ""
                events.append(event)
                event = None

            building_time = True
            time = c + time
        elif c in "omrp" and (building_time or building_time_prefix):
            building_time = False
            building_time_prefix = True
            if event is None:
                event = Goal(int(time), "", "", "")
                time = ""
            event.type = c + event.type
        elif c.isspace() and (building_time or building_time_prefix):
            building_time = False
            building_time_prefix = False
        elif c == "#":
            building_time = False
            event = RedCard(int(time), "", "")
            time = ""
        elif not c.isspace():
            building_time = False
            building_player = True
            if event is None:
                event = Goal(int(time), "", "", "m")
                time = ""
            if space_within_player:
                player = " " + player
                space_within_player = False
            player = c + player
        elif c.isspace() and building_player:
            if not space_within_player:
                space_within_player = True
            else:
                # multiple spaces, assume trailing spaces
                # after visitor with no host following
                last_team = "Visitor"

    if building_player:
        event.player = player
        events.append(event)

    events[0].team = first_team
    events[-1].team = last_team
    return events

def at_number_followed_by_dash(head: str, i: int):
    num = ""
    while i < len(head) and head[i].isdigit():
        num += head[i]
        i += 1

    return not isblank(num) and head[i] == '-'

def parse_score(scoreline: str):
    ret = []
    prev_item = None
    for c in scoreline:
        if prev_item is None:
            prev_item = c
        elif prev_item.isdigit() and c.isdigit():
            prev_item += c
        elif prev_item.isdigit():
            ret.append(prev_item)
            prev_item = c
        elif c.isdigit():
            prev_item = c

    # In match has ended 0-0 or is underway before second half
    # the scoreline ends with visitor goal count instead of ')'
    if prev_item.isdigit():
        ret.append(prev_item)

    # A match ending 0-0 does not have separate first/second half scores
    if ret == ['0', '0']:
        return [0, 0, 0, 0]

    return [int(n) for n in ret]

def list_to_str(list: list):
    return "".join(list)

def get_subpage_count(page: str) -> int:
    head, _ = page.split("\n", maxsplit=1)
    head = head.strip()
    _, count = head.rsplit("/", maxsplit=1)
    return int(count)