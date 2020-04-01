-- SQL file to generate the Database
CREATE TABLE IF NOT EXISTS source(
  id INTEGER PRIMARY KEY,
  name TEXT UNIQUE,
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
  name TEXT UNIQUE,
  category TEXT,
  requirements TEXT,
  description TEXT
);

CREATE TABLE IF NOT EXISTS armour(
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
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

CREATE TABLE IF NOT EXISTS spell(
  'id' INTEGER PRIMARY KEY,
  'name' TEXT UNIQUE,
  'spellike_level' INTEGER,
  'school' TEXT,
  'subschool' TEXT,
  'casting_time' TEXT,
  'components' TEXT,
  'range' TEXT,
  'area' TEXT,
  'effect' TEXT,
  'targets' TEXT,
  'duration' TEXT,
  'saving_throw' TEXT,
  'spell_resistance' TEXT,
  'description' TEXT,
  'description_short' TEXT,
--  'source' TEXT,
--  'mythic_text' TEXT,
--  'mythic_augmentations' TEXT,
--  'haunt_text' TEXT,
'material_costs' INTEGER
);
CREATE TABLE IF NOT EXISTS spell_descriptor(
  id INTEGER PRIMARY KEY,
  spell_id INTEGER,
  descriptor TEXT
);

CREATE TABLE IF NOT EXISTS spell_component(
  id INTEGER PRIMARY KEY,
  spell_id INTEGER,
  component TEXT,
  details TEXT
);

CREATE TABLE IF NOT EXISTS spell_class(
  id INTEGER PRIMARY KEY,
  spell_id INTEGER,
  level INTEGER,
  class_id TEXT -- Change to integer and link when classes have been scraped
);

CREATE TABLE IF NOT EXISTS spell_mythic(
  id  INTEGER PRIMARY KEY,
  spell_id INTEGER,
  description TEXT
);

CREATE TABLE IF NOT EXISTS spell_mythic_augmentation(
  id  INTEGER PRIMARY KEY,
  spell_id INTEGER,
  augmentation_level INTEGER,
  description TEXT
);
