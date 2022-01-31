
from typing import NamedTuple, Optional

class Food(NamedTuple):
  name: str
  category: Optional[int] = None
  rowid: Optional[int] = None

  @staticmethod
  def setup(cursor):
    cursor.execute("""CREATE TABLE IF NOT EXISTS FoodItems (
            rowid INTEGER PRIMARY KEY,
            name TEXT,
            category INTEGER,
            FOREIGN KEY (category) REFERENCES Categories (rowid) ON DELETE SET NULL
        );""")

  @staticmethod
  def __from_row(row):
    name, category, rowid = row
    return Food(name, category, rowid)

  @staticmethod
  def list(cursor):
    cursor.execute("SELECT name, category, rowid FROM FoodItems;")
    for row in cursor:
      yield Food.__from_row(row)

  @staticmethod
  def fetch(cursor, i):
    cursor.execute("SELECT name, category, rowid FROM FoodItems WHERE rowid = ?;", (i,))
    row = cursor.fetchone()
    if row is None:
      return None
    return Food.__from_row(row)

  @staticmethod
  def save(cursor, food):
    if food.rowid is None:
      cursor.execute("INSERT INTO FoodItems (name, category) VALUES (?, ?);", (food.name, food.category,))
      return Food(food.name, food.category, cursor.lastrowid)
    else:
      cursor.execute("UPDATE FoodItems SET name = ?, category = ? WHERE rowid = ?;", (food.name, food.category, food.rowid))
      return food

