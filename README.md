# Yle-ttv-futis-parser

## Overview
A tool to parse football reports fetched from the web version of Yle Teksti-TV to be used within Python programs. For instance recent matches for the English Premier League are reported on page [673](https://yle.fi/aihe/tekstitv?P=673). This tool only parses plain text page content so the fetching of Teksti-TV pages and extracting the plain text representation needs to be done with a different tool such as https://github.com/koponan/yle-ttv.

## Example usage
This tool is intended to be called within a Python application that for instance stores the generated report objects to a
database, but for the sake of demonstration here is a simpler example that reads a page from Teksti-TV and prints a (WIP) string representation of the generated `ttv_parser.models.Report` object.

First requirement is a utility that produces the content of Teksti-TV pages in plain text without ttv formatting for colors etc. This example uses https://github.com/koponan/yle-ttv aliased to 'ttv'. Other Teksti-TV clients may be incompatible with this example.

Second requirement is a script named 'example.py' that has suitable location to find the `ttv_parser` package. The script must have execution permissions and the following content:
```python
#!/usr/bin/env python3

import sys

from ttv_parser import parser

if __name__ == "__main__":
    data_raw = ""
    empty_line_count = 0
    # Reads just first of possibly many matches
    # due to empty line limit 2
    while (empty_line_count < 2):
        data_line = input()
        if not data_line:
            if empty_line_count == 0:
                data_raw += "\n"
            empty_line_count += 1
            continue

        data_raw += data_line + "\n"

    print("> Report...", end="\n\n")
    print(data_raw)
    rep = parser.parse_report(data_raw)
    print("> Parses to...", end="\n\n")
    print(rep)

```

Example run on 2025-01-07 for the English Premier League (page 673) where one match was played the previous day:
```
$ ttv -n 673 | ./example.py
> Report...

   ENGLANTI   VALIOLIIGA  06.01.    1/1 

 Wolverhampton - Nottingham    0-3 (0-2)
                 Gibbs-White  07        
                 Wood         44        
                 Awoniyi      90+4      

> Parses to...

ENGLANTI VALIOLIIGA 2025-01-06 [1, 1]
-------------------------------------
Wolverhampton vs Nottingham 0-3 (0-2) {
    Goal(time=7, player='Gibbs-White', team='Visitor', type='m')
    Goal(time=44, player='Wood', team='Visitor', type='m')
    Goal(time=90+4, player='Awoniyi', team='Visitor', type='m')
}
```