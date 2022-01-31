
from .food import Food
from typing import NamedTuple, Optional

# ConsumedFood is a set of Food.
class ConsumedFood(NamedTuple):
  @staticmethod
  def setup(cursor):
    cursor.execute("""CREATE TABLE IF NOT EXISTS ConsumedFood (
            foodid INTEGER PRIMARY KEY,
            FOREIGN KEY (foodid) REFERENCES FoodItems (rowid) ON DELETE CASCADE
        );""")

  @staticmethod
  def list(cursor):
    cursor.execute("""SELECT name, category, foodid
                      FROM ConsumedFood
                      JOIN FoodItems ON FoodItems.rowid = ConsumedFood.foodid;""")
    for row in cursor:
      yield Food._Food__from_row(row)

  @staticmethod
  def contains(cursor, foodid):
    cursor.execute("SELECT EXISTS(SELECT 1 FROM ConsumedFood WHERE foodid = ?);", (foodid,))
    return cursor.fetchone()[0]

  @staticmethod
  def add(cursor, foodid):
    cursor.execute("INSERT INTO ConsumedFood (foodid) VALUES (?);", (foodid,))

  @staticmethod
  def remove(cursor, foodid):
    cursor.execute("DELETE FROM ConsumedFood WHERE foodid = ?;", (foodid,))

