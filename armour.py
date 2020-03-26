from bs4 import *
import common
import sys

if len(sys.argv) == 1:
    db_path = "pathfinder.sqlite3"
else:
    db_path = sys.argv[1]

def scrape_armour(path):
    conn = common.open_db(db_path)
    db = conn.cursor()
    domain = "https://aonprd.com/"

    categories = ["Light", "Medium", "Heavy", "Sheild"]

    for category in categories:
        armour_list_html = common.get_file(
            domain + "/EquipmentArmor.aspx?Category=" + category
        )
        armourlist_soup = BeautifulSoup(armour_list_html, "html.parser")
        armour_names = set()
        for row in armourlist_soup.find_all("tr"):
            if row.find("td") == None:
                continue
            armour_names.add(row.find("a").get("href"))
        for url in armour_names:
            print(url)
            armour_html = common.get_file(domain + url)
            armour_soup = BeautifulSoup(armour_html, "html.parser")
            td = armour_soup.find("td")
            if td == None:
                print("We've got an issue with " + u)
                continue
            data = {}
            data["name"] = td.find("h1").string
            if data["name"] is None:
                for s in td.find("h1").descendants:
                    if s.string != None:
                        data["name"] = str.lstrip(s.string)
                        break
            main_c = 0
            sources = []
            for child in td.find("span").children:
                for child in td.find("span").children:
                    if child.name == "br" and child.next_sibling.name != "b":
                        main_c = child.next_sibling
                        break
                    if child.name != "b":
                        continue
                    if child.string == "Source":
                        x = child.next_sibling
                        while x.name != "br":
                            if x.name == "a":
                                sources.append([str(x)])  # common.reference(db,x))
                            x = x.next_sibling
                        continue
                    if child.string in [
                        "Cost",
                        "Weight",
                        "Armor Bonus",
                        "Max Dex Bonus",
                        "Armor Check Penalty",
                        "Arcane Spell Failure Chance",
                    ]:
                        array_item = child.string.lower().replace(" ", "_").replace("armor", "arour") # okay that last bit is pedantry, BUT
                        data[array_item] = common.integer_property(child.next_sibling.string)
                        continue
                    if child.string == "Speed":
                        speeds = child.next_sibling.string.split("/")
                        data["speed_30"] = common.integer_property(speeds[0])
                        data["speed_20"] = common.integer_property(speeds[1])
                        continue
                    print(child.string + ": " + child.next_sibling.string)
            data["description"] = ""
            #print(data)
            db.execute("INSERT INTO armour (name, cost, weight, armour_bonus, max_dex, check_pen, arcane_failure_chance, speed_30, speed_20, description) VALUES (:name, :cost, :weight, :armour_bonus, :max_dex, :armour_check_penalty, :arcane_failure_chance, :speed_30, :speed_20, :description);", data)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    scrape_armour(db_path)
