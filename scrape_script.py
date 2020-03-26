#! /usr/bin/env python

from armour import *
from traits import *
from weapons import *

import sys

if len(sys.argv) == 1:
    db_path = "pathfinder.sqlite3"
else:
    db_path = sys.argv[1]

if __name__ == "__main__":
    # Alphabetically ordered
    scrape_armour(db_path)
    scrape_trait(db_path)
