from bs4 import BeautifulSoup
import common
import sys
import time

if len(sys.argv) == 1:
    db_path = "pathfinder.sqlite3"
else:
    db_path = sys.argv[1]

def scrape_type(path):
    conn = common.open_db(db_path)
    db = conn.cursor()
    domain = "https://aonprd.com/"

    category_list_html = common.get_file(domain+"Traits.aspx")
    soup = BeautifulSoup(category_list_html, "html.parser")

    trait_urls = set()

    # for every trait category
    for a in soup.find("div", id="main").descendants:
        if a.name != "a":
            continue
        print(a.string)
        category_html = common.get_file(domain+a.get("href"))
        traitslist_soup = BeautifulSoup(category_html, "html.parser")
        for td in traitslist_soup.find_all("td"):
            a = td.find("a")
            if a != None:
                trait_urls.add(a.get("href"))
    print(len(trait_urls))
    for u in trait_urls:
        print(u)
        trait_html = common.get_file(domain+u);
        trait_soup = BeautifulSoup(trait_html, "html.parser")
        td = trait_soup.find("td")
        if td== None:
            print("We've got an issue with "+u)
            continue
        name =td.find("h1").string
        if name is None:
            for s in td.find("h1").descendants:
                if s.string != None:
                    name = str.lstrip(s.string)
                    break
        print(name)
        print( common.reference(db, td.find("a", class_="external-link")))
    conn.commit()
    conn.close()



if __name__ == "__main__":
    scrape_type(db_path)
