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

    spell_list_html = common.get_file(domain + "/Spells.aspx?Class=All")
    spell_list_soup = BeautifulSoup(spell_list_html, "html.parser")
    spell_names = set()
    for row in spell_list_soup.find_all("tr"):
        if row.find("td") == None:
            continue
        spell_names.add(row.find("a").get("href"))
    print(len(spell_names))
    for url in spell_names:
        print(url)
        spell_html = common.get_file(domain + url)
        spell_soup = BeautifulSoup(spell_html, "html.parser")
        for title in spell_soup.find_all("h1", class_="title"):
            data = {}
            levels = {}
            sources = []
            data["name"] = title.string
            if data["name"] is None:
                for s in title.descendants:
                    if s.string != None:
                        data["name"] = str.lstrip(s.string)
                        break
            e = title.next_sibling
            while e != None and e.name != "h1":
                if e.name == "h3" and e.string == "Description":
                    e=e.next_sibling
                    break
                if e.name == "b":
                    s = e.string
                    e = e.next_sibling
                    if s == "Source":
                        while e.name != "br":
                            if e.name == "a":
                                print(e)
                            e = e.next_sibling
                        continue
                    if s == "School":
                        data["school"] = e.string
                        continue
                    if s == "Level":
                        q = e.string.split(",")
                        print(q)
                        continue
                    print("\t"+s+": "+e.string)
                print(e)
                e = e.next_sibling
            desc_str = ""
            while e != None and e.name != "h1":
                desc_str +=str(e)
                e=e.next_sibling
            print(desc_str)
            data["description"] = common.cleanup_html(desc_str)
            print(data)
            print(sources)
        break
    conn.commit()
    conn.close()


if __name__ == "__main__":
    scrape_armour(db_path)
