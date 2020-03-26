# common.py - procides caching for web scraping to not be a dick

import requests
import os
import re  # eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
import sqlite3


def url_esc(url):
    return url.replace("/", "_")


def get_file(*parts):
    url = os.path.join(*parts)
    
    if not os.path.exists("__scraping_cache__"):
        os.mkdir("__scraping_cache__")
    if not os.path.exists("__scraping_cache__/" + url_esc(url)):
        request = requests.get(url)
        file_content = (
            request.content.decode(request.encoding)
            .encode("ascii", "xmlcharrefreplace")
            .decode("ascii")
        )
        f = open("__scraping_cache__/" + url_esc(url), "w+")
        f.write(file_content)
        f.close()
        return file_content
    else:
        f = open("__scraping_cache__/" + url_esc(url), "r")
        file_content = f.read()
        f.close()
        return file_content


def open_db(path):
    if os.path.isfile(path):
        return sqlite3.connect(path)
    else:
        conn = sqlite3.connect(path)
        # We Have to execute some SQL on this
        db = conn.cursor()
        with open("D&Db.sql", "r") as file:
            data = file.read()
            db.executescript(data)
        return conn


def integer_property(x):
    fixed_string = re.sub("[,;%]", "", x).replace("- ", "-")
    strings = fixed_string.split(" ")
    for s in strings:
        if s != "":
            if s == "—":
                return None
            else:
                return int(s)


def reference(db, link):
    s = link.string
    q = s.split(" pg. ")
    db.execute("SELECT id from source WHERE name = ?;", (q[0],))
    rows = db.fetchall()
    if len(rows) == 0:
        db.execute(
            "INSERT INTO source (name, url) VALUES (?,?);", [q[0], link.get("href")]
        )
        db.execute("SELECT last_insert_rowid();")
        rows = db.fetchall()
    return [rows[0][0], int(q[1])]


def cleanup_html(string):
    # stub, to be fixed later
    return string
