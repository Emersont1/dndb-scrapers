-- SQL file to generate the Database
CREATE TABLE IF NOT EXISTS source(
  id INTEGER PRIMARY KEY,
  name TEXT,
  url TEXT
);

CREATE TABLE IF NOT EXISTS reference(
    id INTEGER PRIMARY KEY,
    table_name TEXT,
    source INTEGER,
    page INTEGER,
    destination INTEGER
);

CREATE TABLE IF NOT EXISTS trait(
  id INTEGER PRIMARY KEY,
  name TEXT,
  category TEXT,
  requirements TEXT,
  description TEXT
);

CREATE TABLE IF NOT EXISTS armour(
    id INTEGER PRIMARY KEY,
    name TEXT,
    cost INTEGER,
    weight INTEGER,
    armour_bonus INTEGER,
    max_dex INTEGER,
    check_pen INTEGER,
    arcane_failure_chance INTEGER,
    speed_30 INTEGER,
    speed_20 INTEGER,
    description TEXT
);
