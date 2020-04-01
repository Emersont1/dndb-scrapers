import lxml.html
import html
import re
import common
import spell_arrays
import sqlite3
import sys

if len(sys.argv) == 1:
    db_path = "pathfinder.sqlite3"
else:
    db_path = sys.argv[1]


def scrape_spells(path):
    connection = common.open_db(path)
    # Open Database
    domain = "https://aonprd.com/"
    db = connection.cursor()


    # List of all spells at https://aonprd.com/spells.aspx?Class=All
    doc = lxml.html.fromstring(
        common.get_file(domain + "Spells.aspx?Class=All").encode("ascii")
    )
    urls = []
    s_descs = {}
    for f in doc.xpath("//td/span[contains(@id, 'ctl00_MainContent_DataListTypes_ctl')]"):
        urls.append(f.xpath("b/a/@href")[0])
        v = lxml.html.tostring(f).decode("ascii")
        u = "".join(re.split("<[/]?i>|</span>", v))
        i = u.find(">:")
        j = u.find("<br>")
        # print(i)
        s_descs[f.xpath("b/a/text()")[0].strip()] = u[i + 3 : j]
    # print(s_descs)

    # now iterate over rows in the table
    for f in urls:
        print("== " + f)
        b = common.get_file(domain + f).encode("ascii")
        doc = lxml.html.fromstring(b)
        # x = inner_html(doc.xpath("//span[contains(@id, 'ctl00_MainContent_DataListTypes_ctl')]")[0]);

        # process the HTML

        x = lxml.html.tostring(
            doc.xpath("//span[contains(@id, 'ctl00_MainContent_DataListTypes_ctl')]")[0]
        ).decode("utf-8")
        # print(x)
        # break
        for o_html in x.split("<h1")[1:]:
            # if not spell_html:
            #    continue
            spell_html = "<h1" + o_html.split('<h2 class="title">')[0]
            # print(spell_html)
            spell = lxml.html.fromstring(spell_html)
            name = "".join(spell.xpath("//h1/text()")).strip()
            try:
                db.execute(
                    "INSERT INTO spell (name, material_costs) VALUES (?, 0);", [name]
                )
            except sqlite3.Error as err:
                print(err)
                continue
            row_id = db.lastrowid
            if name in s_descs.keys():
                db.execute(
                    "UPDATE spell SET description_short = ? WHERE id = ?",
                    [s_descs[name], row_id],
                )
            # row["description_formated"] = spell_html
            html_sans_header = spell_html.split("</h1>")[1].replace("<br><b></b>", "; 23")
            next_needs_prefix_h3 = False
            next_needs_prefix_b = False
            desc_done = False

            for f in filter(None, re.split("(<h3|<b>)+", html_sans_header)):
                h3 = False
                b = False
                if f == "<h3":
                    next_needs_prefix_h3 = True
                    continue
                if f == "<b>":
                    next_needs_prefix_b = True
                    continue
                if f == "<br>":
                    continue
                if f == "<b></b> <br>":
                    continue
                if next_needs_prefix_h3:
                    next_needs_prefix_h3 = False
                    f = "<h3" + f
                    h3 = True
                if next_needs_prefix_b:
                    next_needs_prefix_b = False
                    f = "<b>" + f
                    b = True
                # now read it as HTML
                # print(f)
                row_html = lxml.html.fromstring(f)
                if b and not desc_done:
                    try:
                        title = row_html.xpath("//b/text()")[0].strip()
                    except IndexError:
                        print(f)
                        continue
                    # if title == this:...
                    if title == "School":
                        # boy this needs some processing
                        # print(f)
                        a = row_html.xpath("text()")[0].strip()
                        # print(re.split(";| ",a))
                        school = list(filter(None, re.split(";| ", a)))[0]
                        # print(list(filter(None, re.split(";| ",a)))[0])
                        if school == "multiple":
                            school = "multiple (see text)"
                            # print(a[len(row["school"]):])
                        else:
                            u = a[len(school) :]
                            if u != ";" and u != "":
                                data = list(filter(None, re.split("\s?[\[\]\(\)]\s?", u)))
                                db.execute(
                                    "UPDATE spell SET subschool = ? WHERE id = ?",
                                    [data[0], row_id],
                                )
                                if len(data) > 1:
                                    descriptor = data[1].replace("-", "_").lstrip()
                                    # db.execute("UPDATE spell SET descriptor = ? WHERE id = ?",[descriptor, row_id])
                                    for eff in descriptor.split(","):
                                        if eff == ";":
                                            continue
                                        eff = str.strip(eff)
                                        db.execute(
                                            "INSERT INTO spell_descriptor (descriptor, spell_id) VALUES (?, ?);",
                                            [eff, row_id],
                                        )
                        db.execute(
                            "UPDATE spell SET school = ? WHERE id = ?", [school, row_id]
                        )
                        continue
                    if title == "Source":

                        # u = row_html.xpath("a/i/text()")[0]
                        # db.execute("UPDATE spell SET source = ? WHERE id = ?",[u[:u.find("pg.")-1], row_id])
                        continue
                    ##HERE
                    if title == "Level":
                        u = (
                            row_html.xpath("text()")[0]
                            .replace(" (unchained)", "_unchained")
                            .split("(")[0]
                        )
                        sl_level = 9
                        w_level = False
                        for l in u.strip().split(", "):
                            class_nm = l.split(" ")[0]
                            try:
                                lvl = int(l.split(" ")[1])
                            except IndexError:
                                print(l)
                                print(f)
                            if not w_level:
                                sl_level = min(sl_level, lvl)
                            if class_nm == "wizard" or class_nm == "sorcerer":
                                w_level = True
                                sl_level = lvl
                            # if class_nm == "sorcerer":
                            #    class_nm = "sor"
                            db.execute(
                                "INSERT INTO spell_class (spell_id, class_id, level) VALUES (?,?,?)",
                                [row_id, class_nm, lvl],
                            )
                        db.execute(
                            "UPDATE spell SET spellike_level = ? WHERE id = ?;",
                            [sl_level, row_id],
                        )
                        continue
                    if title == "Casting Time":
                        db.execute(
                            "UPDATE spell SET casting_time = ? WHERE id = ?;",
                            [row_html.xpath("text()")[0].lstrip(), row_id],
                        )
                        continue
                    if title == "Components":
                        components = row_html.xpath("text()")[0].lstrip()
                        for comp in re.split("[ /,]+", components):
                            # print("\""+comp+"\"")
                            if comp == "V":
                                db.execute(
                                    "INSERT INTO spell_component (component, spell_id) VALUES ('verbal', ?);",
                                    [row_id],
                                )
                            if comp == "S":
                                db.execute(
                                    "INSERT INTO spell_component (component, spell_id) VALUES ('somatic', ?);",
                                    [row_id],
                                )
                            if comp == "M":
                                u = re.split("[\\(\\)]", components)
                                if len(u) == 1:
                                    u.append(None)
                                print(u)
                                db.execute(
                                    "INSERT INTO spell_component (component, spell_id, details) VALUES ('material', ?, ?);",
                                    [row_id, u[1]],
                                )
                                if u[1] != None:
                                    p = re.search("([0-9]+) gp", u[1].replace(",", ""))
                                    print(p)
                                    if p:
                                        db.execute(
                                            "UPDATE spell SET material_costs = ? WHERE id = ?;",
                                            [p.group(1), row_id],
                                        )
                                        db.execute(
                                            "INSERT INTO spell_descriptor (descriptor, spell_id) VALUES ('costly_components', ?);",
                                            [row_id],
                                        )
                            if comp == "F":
                                db.execute(
                                    "INSERT INTO spell_component (component, spell_id) VALUES ('focus', ?);",
                                    [row_id],
                                )
                            if comp == "DF":
                                db.execute(
                                    "INSERT INTO spell_component (component, spell_id) VALUES ('divine_focus', ?);",
                                    [row_id],
                                )
                        continue
                    if title in [
                        "Target",
                        "Targets",
                        "Target or Targets",
                        "Targt",
                        "Targts",
                        "Targer",
                    ]:
                        db.execute(
                            "UPDATE spell SET targets = ? WHERE id = ?;",
                            [row_html.xpath("text()")[0].lstrip(), row_id],
                        )
                        continue
                    if title == "Effect" or title == "Efect":
                        db.execute(
                            "UPDATE spell SET effect = ? WHERE id = ?;",
                            [row_html.xpath("text()")[0].lstrip(), row_id],
                        )
                        continue
                    if title == "Range":
                        db.execute(
                            "UPDATE spell SET range = ? WHERE id = ?;",
                            [row_html.xpath("text()")[0].lstrip(), row_id],
                        )
                        continue
                    if title == "Area":
                        db.execute(
                            "UPDATE spell SET area = ? WHERE id = ?;",
                            [row_html.xpath("text()")[0].lstrip(), row_id],
                        )
                        continue
                    if title == "Target, Effect, or Area":
                        db.execute(
                            "UPDATE spell SET targets = ?1,effect = ?1,area = ?1 WHERE id = ?2;",
                            [row_html.xpath("text()")[0].lstrip(), row_id],
                        )
                        continue
                    if title == "Area or Target" or title == "Target or Area":
                        db.execute(
                            "UPDATE spell SET targets = ?1,area = ?1 WHERE id = ?2;",
                            [row_html.xpath("text()")[0].lstrip(), row_id],
                        )
                        continue
                    if title == "Target/Effect":
                        db.execute(
                            "UPDATE spell SET targets = ?1,effect = ?1 WHERE id = ?2;",
                            [row_html.xpath("text()")[0].lstrip(), row_id],
                        )
                        continue
                    if title == "Duration":
                        dur = row_html.xpath("text()")[0].lstrip()
                        if dur[-4:] == " (D)":
                            dur = dur[:-4]
                            db.execute(
                                "INSERT INTO spell_descriptor (descriptor, spell_id) VALUES ('dismissible', ?);",
                                [row_id],
                            )
                        db.execute(
                            "UPDATE spell SET duration = ? WHERE id = ?;", [dur, row_id]
                        )
                        continue
                    if title == "Saving Throw":
                        db.execute(
                            "UPDATE spell SET saving_throw = ? WHERE id = ?;",
                            [row_html.xpath("text()")[0].lstrip(), row_id],
                        )
                        continue
                    if title == "Spell Resistance":
                        db.execute(
                            "UPDATE spell SET spell_resistance = ? WHERE id = ?;",
                            [row_html.xpath("text()")[0].lstrip(), row_id],
                        )
                        continue
                    print('"' + title + '"')
                if h3:
                    title = row_html.xpath("//h3/text()")[0]
                    # print(title.encode('unicode-escape'))
                    if title == "Description":
                        desc_done = True
                        d1 = html_sans_header[
                            html_sans_header.find("Description</h3>")
                            + len("Description</h3>") : html_sans_header.find(
                                '<h2 class="title">'
                            )
                        ]
                        d2 = re.split("<[/]?i>|<[/]?b>|</span>", d1)
                        desc = (
                            html.unescape("".join(d2))
                            .rstrip()
                            .replace("<br>", "\\n")
                            .replace("<h2>", "\\n")
                            .replace("</h2>", ": ")
                            .replace('<h3 class="framing">', "\\n")
                            .replace("</h3>", ": ")
                        )
                        db.execute(
                            "UPDATE spell SET description = ? WHERE id = ?;", [desc, row_id]
                        )
                    if title == "Haunt Statistics" and False:
                        haunt_s = ""
                        for string in filter(
                            None,
                            re.split(
                                "<[/]?b>|</span>",
                                html_sans_header.split(
                                    '<h3 class="framing">Haunt Statistics</h3>'
                                )[1].replace("<br>", "\\n"),
                            ),
                        ):
                            s = string.strip()
                            haunt_s += s
                            if s[-2:] != "\\n" and s[-1:] != ";":
                                haunt_s += ": "
                            if s[-1:] == ";":
                                haunt_s += " "
                        haunt_s = haunt_s[:-4]
                        db.execute(
                            "UPDATE spell SET haunt_text = ? WHERE id = ?;",
                            [haunt_s, row_id],
                        )

            # now deal with any <h2>s
            if len(o_html.split('<h2 class="title">')) > 1:
                mythic_text = o_html.split('<h2 class="title">')[1]
                mythic_text = mythic_text[: mythic_text.find("</h2>")]
                if mythic_text == "Mythic " + name:
                    db.execute(
                        "INSERT INTO spell_descriptor (descriptor, spell_id) VALUES ('mythic', ?);",
                        [row_id],
                    )
                    a = o_html.split("</h2>")[1].strip()
                    v = html.unescape(a[a.find("<br>") + 4 :])
                    u = v.split("<b>")[0].replace("<br>", "\n").strip().replace("\n", "\\n")
                    if u[-7:] == "</span>":
                        mythic_text = u[:-7]
                    else:
                        mythic_text = u
                    # print(row["mythic_text"])

                    if v.find("Augmented") != -1:
                        for t in v.split("Augmented"):
                            mythics = {"spell_id": row_id}
                            levels = []
                            if t.find(")") != -1:
                                levels = re.findall(r"(\d+)(th|st|rd)", t[: t.find(")")])
                            if len(levels) != 0:
                                mythics["level"] = levels[0][0]
                                mythics["text"] = str.lstrip(t[t.find(":") + 1 :])
                            else:
                                # print(print(t[t.find(")")]))
                                # print(t)
                                mythics["level"] = 1
                                mythics["text"] = str.lstrip(t[t.find(":") + 1 :])
                                # input("")
                            if mythics["text"][-12:] == " <br><br><b>":
                                mythics["text"] = mythics["text"][:-12]
                            print(mythics)
                            db.execute(
                                "INSERT INTO spell_mythic_augmentation (description, spell_id, augmentation_level) VALUES (:text, :spell_id, :level);",
                                mythics,
                            )

                db.execute(
                    "INSERT INTO spell_mythic (description, spell_id) VALUES (?,?);",
                    [mythic_text, row_id],
                )


    connection.commit()
    connection.close()

if __name__ == "__main__":
    scrape_spells(db_path)
