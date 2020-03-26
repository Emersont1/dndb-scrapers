import common
import sys

if len(sys.argv) == 1:
    db_path = "pathfinder.sqlite3"
else:
    db_path = sys.argv[1]


def scrape_type(path):
    conn = common.open_db(path)


if __name__ == "__main__":
    scrape_type(db_path)
