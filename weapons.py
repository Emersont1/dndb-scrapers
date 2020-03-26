from bs4 import *
import common
import sys

if len(sys.argv) == 1:
    db_path = "pathfinder.sqlite3"
else:
    db_path = sys.argv[1]


def damage_type(string):
    qty = 0
    print
    for x in string.replace(";", "").split(" "):
        if x == "":
            continue
        if x == "B":
            qty ^= 1
            continue
        elif x == "P":
            qty ^= 2
            continue
        elif x == "S":
            qty ^= 4
            continue
        elif x.lower() in ["and", "&"]:
            qty ^= 8
            continue
        elif x.lower() == "or":
            continue
    return qty


def scrape_weapon(path):
    conn = common.open_db(path)
    db = conn.cursor()
    domain = "https://aonprd.com/"

    prociciencies = ["Simple", "Martial", "Exotic", "Ammo"]
    weapon_links = set()
    for p in prociciencies:
        weapon_list_html = common.get_file(
            domain + "/EquipmentWeapons.aspx?Proficiency=" + p
        )
        weapon_list_soup = BeautifulSoup(weapon_list_html, "html.parser")
        for row in weapon_list_soup.find_all("tr"):
            if row.find("td") == None:
                continue
            weapon_links.add(row.find("a").get("href"))

    for link in weapon_links:
        print(link)
        weapon_html = common.get_file(domain + link)
        weapon_soup = BeautifulSoup(weapon_html, "html.parser")
        data = {}
        td = weapon_soup.find("td")
        if td == None:
            print("We've got an issue with " + u)
            continue
        data = {
            "dmg_s": None,
            "dmg_m": None,
            "dmg_type": None,
            "critical": None,
            "range": None,
            "special": None,
        }
        sources = []
        groups = []
        data["name"] = td.find("h1").string
        if data["name"] is None:
            for s in td.find("h1").descendants:
                if s.string != None:
                    data["name"] = str.lstrip(s.string)
                    break
        for child in td.find("span").children:
            if child.name != "b":
                continue
            if child.string == "Source":
                x = child.next_sibling
                while x.name != "h3":
                    if x.name == "a":
                        sources.append(common.reference(db, x))
                    x = x.next_sibling
                continue
            if child.string in ["Cost", "Weight", "Range"]:
                array_item = child.string.lower().replace(" ", "_")
                data[array_item] = common.integer_property(child.next_sibling.string)
                continue
            if child.string in ["Proficiency", "Critical", "Category", "Special"]:
                array_item = child.string.lower().replace(" ", "_")
                data[array_item] = str.strip(child.next_sibling.string).replace(";", "")
                if data[array_item] == "—":
                    data[array_item] = None
                continue
            if child.string == "Damage":
                a = child.next_sibling.string.split(" ")
                data["dmg_s"] = a[1]
                data["dmg_m"] = a[3]
                if data["dmg_s"] == "—":
                    data["dmg_s"] = None
                if data["dmg_m"] == "—":
                    data["dmg_m"] = None
                continue
            if child.string == "Type":
                data["dmg_type"] = damage_type(child.next_sibling.string)
                continue
            if child.string == "Weapon Groups":
                a = child.next_sibling
                while a.name not in ["h3", "b"]:
                    if a.name == "a":
                        groups.append(a.string)
                    a = a.next_sibling
                continue
            print(child.string + ": " + child.next_sibling.string)
        my_str = ""
        u = None
        for header in td.find_all("h3"):
            if header.string == "Description":
                u = header.next_sibling
        while u != None:
            my_str += str(u)
            u = u.next_sibling
        data["description"] = common.cleanup_html(my_str)
        print(data)
        db.execute(
            "INSERT INTO weapon(name, cost, weight, dmg_s, dmg_m, dmg_type, critical, range, special, category, proficiency, description) VALUES(:name, :cost, :weight, :dmg_s, :dmg_m, :dmg_type, :critical, :range, :special, :category, :proficiency, :description);",
            data,
        )
        db.execute("SELECT last_insert_rowid();")
        rows = db.fetchall()
        i = rows[0][0]
        for x in sources:
            x.append(i)
            db.execute(
                "INSERT INTO reference (table_name, source, page, destination) VALUES ('weapon', ?, ?, ?);",
                x,
            )
        for x in groups:
            db.execute(
                "INSERT INTO weapon_group (weapon_id, group_name) VALUES ( ?, ?);",
                [i, x],
            )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    scrape_weapon(db_path)
