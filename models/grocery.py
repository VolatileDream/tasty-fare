
from .food import Food
from typing import NamedTuple, Optional

# Grocery is a set of Food.
class Grocery(NamedTuple):
  id: int

  @staticmethod
  def setup(cursor):
    cursor.execute("""CREATE TABLE IF NOT EXISTS Groceries (
            foodid INTEGER PRIMARY KEY
            FOREIGN KEY (foodid) REFERENCES FoodItems (rowid) ON DELETE CASCADE
        );""")

  @staticmethod
  def list(cursor):
    cursor.execute("""SELECT foodid, name, category
                      FROM Groceries
                      JOIN FoodItems ON FoodItems.rowid = ConsumedFood.foodid;""")
    for row in cursor:
      yield Food._Food__from_row(row)

  @staticmethod
  def add(cursor, foodid):
    cursor.execute("INSERT INTO Groceries (foodid) VALUES (?);", (foodid,))

  @staticmethod
  def remove(cursor, foodid):
    cursor.execute("DELETE FROM Groceries WHERE foodid = ?;", (foodid,))

