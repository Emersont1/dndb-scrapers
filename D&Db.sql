-- SQL file to generate the Database
CREATE TABLE IF NOT EXISTS source(
  id INTEGER PRIMARY KEY,
  name TEXT,
  url TEXT
);

CREATE TABLE IF NOT EXISTS trait(
  id INTEGER PRIMARY KEY,
  name TEXT,
  category TEXT,
  requirements TEXT,
  description TEXT,
  -- sources
  source INTEGER, page INTEGER
)
