
from typing import NamedTuple, Optional

class ProductCodeMapping(NamedTuple):
  upc: int
  food: int

  @staticmethod
  def __from_row(row):
    code, food = row
    return ProductCodeMapping(code, food)

  @staticmethod
  def setup(cursor):
    cursor.execute("""CREATE TABLE IF NOT EXISTS ProductCodes (
            code INTEGER PRIMARY KEY ON CONFLICT REPLACE,
            foodid INTEGER,
            FOREIGN KEY (foodid) REFERENCES FoodItems (rowid) ON DELETE RESTRICT
        );""")

  @staticmethod
  def list(cursor):
    cursor.execute("SELECT code, foodid FROM ProductCodes;")
    for row in cursor:
      yield ProductCodeMapping.__from_row(row)

  @staticmethod
  def update_map(cursor, code, food):
    cursor.execute("INSERT INTO ProductCodes (code, foodid) VALUES (?, ?);", (code, food,))
    return ProductCodeMapping(code, food)

  @staticmethod
  def lookup(cursor, code):
    cursor.execute("SELECT code, foodid FROM ProductCodes WHERE code = ?;", (code,))
    row = cursor.fetchone()
    if row is None:
      return None
    return ProductCodeMapping.__from_row(row)
