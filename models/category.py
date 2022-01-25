
from typing import NamedTuple, Optional

class Category(NamedTuple):
  name: str
  id: Optional[int]

  @staticmethod
  def __from_row(row):
    return Category(row['name'], row['rowid'])

  @staticmethod
  def setup(cursor):
    cursor.execute("""CREATE TABLE IF NOT EXISTS Categories (
            rowid INTEGER PRIMARY KEY,
            name TEXT
        );""")
    cursor.execute("SELECT COUNT(*) = 0 FROM Categories;")
    zero = cursor.fetchone()[0]
    if zero:
      # We always want this item at the end of the Categories list.
      cursor.execute("INSERT INTO Categories (name) VALUES ('[Garbage]');")

  @staticmethod
  def list(cursor):
    cursor.execute("SELECT rowid, name FROM Categories;")
    for row in cursor:
      yield Category.__from_row(row)

  @staticmethod
  def fetch(cursor, i):
    cursor.execute("SELECT rowid, name FROM Categories WHERE rowid = ?;", (i,))
    row = cursor.fetchone()
    if row is None:
      return None
    return Category.__from_row(row)

  @staticmethod
  def save(cursor, category):
    if category.rowid is None:
      cursor.execute("INSERT INTO Categories (name) VALUES (?);", (category.name,))
      return Category.__from_row(category.name, cursor.lastrowid)
    else:
      cursor.execute("UPDATE Categories SET (name) VALUES (?) WHERE rowid = ?;", (category.name, category.rowid,))
      return category

