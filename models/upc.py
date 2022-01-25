
from typing import NamedTuple, Optional

class ProductCodeMapping(NamedTuple):
  upc: int
  food: int

  @staticmethod
  def __from_row(row):
    return ProductCodeMapping(row['code'], row['foodid'])

  @staticmethod
  def setup(cursor):
    cursor.excute("""CREATE TABLE IF NOT EXISTS ProductCodes (
            code INTEGER PRIMARY KEY ON CONFLICT REPLACE,
            foodid INTEGER,
            FOREIGN KEY (foodid) REFERENCES FoodItems (rowid) ON DELETE ERROR
        );""")

  @staticmethod
  def list(cursor):
    cursor.execute("SELECT code, foodid FROM ProductCodes;")
    for row in cursor:
      yield ProductCodeMapping.__from_row(row)

  @staticmethod
  def update_map(cursor, code, food):
    cursor.execute("INSERT INTO ProductCodes (code, foodid) VALUES (?, ?);", (code, food,))
