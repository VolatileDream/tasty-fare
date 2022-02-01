
from typing import NamedTuple, Optional

class Category(NamedTuple):
  name: str
  rowid: Optional[int] = None

  # This is here as a constant.
  # It can never be changed.
  GARBAGE = 1

  @staticmethod
  def __from_row(row):
    name, rowid = row
    return Category(name, rowid)

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
      cursor.execute("INSERT INTO Categories (name, rowid) VALUES ('[Garbage]', ?);", (Category.GARBAGE,))

  @staticmethod
  def list(cursor):
    cursor.execute("SELECT name, rowid FROM Categories;")
    for row in cursor:
      yield Category.__from_row(row)

  @staticmethod
  def fetch(cursor, i):
    cursor.execute("SELECT name, rowid FROM Categories WHERE rowid = ?;", (i,))
    row = cursor.fetchone()
    if row is None:
      return None
    return Category.__from_row(row)

  @staticmethod
  def delete(cursor, rowid):
    if rowid == Category.GARBAGE:
      raise Exception("Can not delete category '[Garbage]'")
    cursor.execute("DELETE FROM Categories WHERE rowid = ?;", (rowid,))

  @staticmethod
  def save(cursor, category):
    if category.rowid is None:
      cursor.execute("INSERT INTO Categories (name) VALUES (?);", (category.name,))
      return Category(category.name, cursor.lastrowid)
    elif category.rowid == Category.GARBAGE:
      raise Exception("Can not rename category '[Garbage]'")
    else:
      cursor.execute("UPDATE Categories SET name = ? WHERE rowid = ?;", (category.name, category.rowid,))
      return category

