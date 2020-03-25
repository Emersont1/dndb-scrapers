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
        data = {}
        data["name"] =td.find("h1").string
        if data["name"] is None:
            for s in td.find("h1").descendants:
                if s.string != None:
                    data["name"] = str.lstrip(s.string)
                    break

        source = common.reference(db, td.find("a", class_="external-link"))
        data["source"] = source[0]
        data["page"] = source[1]
        data["requirements"] = None
        main_c = 0
        for child in td.find("span").children:
            if child.name == "br" and child.next_sibling.name != "b":
                main_c = child.next_sibling
                break
            if child.name != "b":
                continue
            if child.string == "Source":
                # already processed
                continue
            if child.string == "Category":
                data["category"] = str.lstrip(child.next_sibling.string)
                continue
            if child.string == "Requirement(s)":
                data["requirements"] = str.lstrip(child.next_sibling.string)
                continue
            print(child.string +": " + child.next_sibling.string)
        my_str = str(main_c)

        while main_c.next_sibling != None:
            main_c = main_c.next_sibling
            my_str += str(main_c)

        data["description"] = common.cleanup_html(my_str)
        db.execute("INSERT INTO trait(name, category, requirements, description, source, page) VALUES (:name, :category, :requirements, :description, :source, :page);", data)
    conn.commit()
    conn.close()



if __name__ == "__main__":
    scrape_type(db_path)
