
import sqlite3

def database(location=":memory:"):
  db = sqlite3.connect(location, isolation_level=None)
  db.execute("PRAGMA foreign_keys = ON;")
  return db
