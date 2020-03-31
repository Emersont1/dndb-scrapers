from bs4 import *
import common
import sys

if len(sys.argv) == 1:
    db_path = "pathfinder.sqlite3"
else:
    db_path = sys.argv[1]


def scrape_armour(path):
    conn = common.open_db(path)
    db = conn.cursor()
    domain = "https://aonprd.com/"
    if True:
        spell_list_html = common.get_file(domain + "/Spells.aspx?Class=All")
        spell_list_soup = BeautifulSoup(spell_list_html, "html.parser")
        spell_names = set()
        for row in spell_list_soup.find_all("tr"):
            if row.find("td") == None:
                continue
            spell_names.add(row.find("a").get("href"))
    else:
        spell_names = ["/SpellDisplay.aspx?ItemName=Cup of Dust"]
    print(len(spell_names))
    for url in spell_names:
        print(url)
        spell_html = common.get_file(domain + url)
        spell_soup = BeautifulSoup(spell_html, "html.parser")
        for title in spell_soup.find_all("h1", class_="title"):
            data = {}
            spell_levels = []
            sources = []
            components = []
            mythic_data = {}
            mythic_sources = []

            data["name"] = title.string
            if data["name"] is None:
                for s in title.descendants:
                    if s.string != None:
                        data["name"] = str.lstrip(s.string)
                        break
            e = title.next_sibling
            while e != None and e.name != "h1":
                if e.name == "h3" and e.string == "Description":
                    e = e.next_sibling
                    break
                if e.name == "br":
                    e = e.next_sibling
                    continue
                if e.name == "b":
                    s = e.string
                    e = e.next_sibling
                    if s == "Source":
                        while e.name != "br":
                            if e.name == "a":
                                sources.append(common.reference(db, e))
                            e = e.next_sibling
                    elif s == "School":
                        # do subschool
                        data["school"] = e.string
                    elif s == "Components":
                        without_brackets = e.string[: e.string.find("(")]
                        # e.string[e.string.find("(")+1:-1]
                        for comp in e.string.split(","):
                            if comp == "":
                                continue
                            c_trim = str.strip(comp)
                            if c_trim == "V":
                                components.append(["Verbal"])
                            elif c_trim == "S":
                                components.append(["Somatic"])
                            elif c_trim[0] == "M":
                                arr = ["Material"]
                                if c_trim.find("(") != -1:
                                    arr.append(c_trim[c_trim.find("(") + 1 : -1])
                                components.append(arr)
                            print(c_trim)
                    elif s == "Level":
                        for spell_level in e.string.split(","):
                            n = ["", -1]
                            for m in spell_level.split(" "):
                                if common.is_int(m):
                                    n[1] = int(m)
                                else:
                                    n[0] += m
                            spell_levels.append(n)
                    elif s in [
                        "Casting Time",
                        "Range",
                        "Area",
                        "Duration",
                        "Saving Throw",
                        "Spell Resistance",
                        "Target",
                    ]:
                        array_name = s.lower().replace(" ", "_")
                        data[array_name] = str.strip(e.string)
                        if data[array_name][-1] == ";":
                            data[array_name] = data[array_name][:-1]
                    else:
                        print(s)
                        print(e.string)
                    e = e.next_sibling
                    continue
                print(e)
                e = e.next_sibling
            desc_str = ""
            while e != None and e.name != "h1" and e.name != "h2":
                desc_str += str(e)
                e = e.next_sibling
            if e.string[:6] == "Mythic":
                mythic_data["name"] = data["name"]
                if e.next_sibling.string == "Source":
                    while e.name != "br":
                        if e.name == "a":
                            mythic_sources.append(common.reference(db, e))
                        e = e.next_sibling
                desc_str = ""
                e = e.next_sibling
                while e != None and e.name != "h1" and e.name != "h2":
                    desc_str += str(e)
                    e = e.next_sibling
                mythic_data["description"] = common.cleanup_html(desc_str)
            data["description"] = common.cleanup_html(desc_str)
            print(data)
            db.execute("INSERT INTO spell(name) VALUES (:name);", data)
            db.execute("SELECT last_insert_rowid();")
            rows = db.fetchall()
            i = rows[0][0]
            for x in sources:
                x.append(i)
                db.execute(
                    "INSERT INTO reference (table_name, source, page, destination) VALUES ('spell', ?, ?, ?);",
                    x,
                )
            for l in spell_levels:
                l.append(i)
                db.execute(
                    "INSERT INTO spell_class (class_id, level, spell_id) VALUES (?,?,?);",
                    l,
                )

            if mythic_data != {}:
                mythic_data["spell_id"] = i
                db.execute(
                    "INSERT INTO spell_mythic(spell_id, description) VALUES (:spell_id, :description);",
                    mythic_data,
                )
                db.execute("SELECT last_insert_rowid();")
                rows = db.fetchall()
                i = rows[0][0]
                for x in mythic_sources:
                    x.append(i)
                    db.execute(
                        "INSERT INTO reference (table_name, source, page, destination) VALUES ('spell_mythic', ?, ?, ?);",
                        x,
                    )
            print(components)
            print(mythic_data)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    scrape_armour(db_path)
