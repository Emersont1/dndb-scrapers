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

CREATE TABLE IF NOT EXISTS weapon(
  id INTEGER PRIMARY KEY,
  name TEXT,
  cost INTEGER,
  weight REAL,
  dmg_s TEXT,
  dmg_m TEXT,
  dmg_type INTEGER,
  critical TEXT,
  range INTEGER,
  special TEXT,
  category TEXT,
  proficiency TEXT,
  description TEXT
);

CREATE TABLE IF NOT EXISTS weapon_group(
  id INTEGER PRIMARY KEY,
  weapon_id INTEGER,
  group_name TEXT
);
