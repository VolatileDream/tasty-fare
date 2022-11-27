
from .food import Food
from typing import NamedTuple, Optional

class Recipe(NamedTuple):
  name: str
  rowid: Optional[int] = None

  @staticmethod
  def setup(cursor):
    # To generalize, maybe this should include an "instructions" field?
    cursor.execute("""CREATE TABLE IF NOT EXISTS Recipes (
            rowid INTEGER PRIMARY KEY,
            name TEXT
        );""")
    # Cascade all deletions, force callers to look at items it contains.
    # We use ON CONFLICT REPLACE, because in the future we might want to
    # add other fields such as "quantity" to the table.
    cursor.execute("""CREATE TABLE IF NOT EXISTS RecipeContents (
            foodid INTEGER,
            recipe_id INTEGER,
            PRIMARY KEY (recipe_id, foodid) ON CONFLICT REPLACE,
            FOREIGN KEY (foodid) REFERENCES FoodItems (rowid) ON DELETE CASCADE,
            FOREIGN KEY (recipe_id) REFERENCES Recipes (rowid) ON DELETE CASCADE
        );""")

  @staticmethod
  def __from_row(row):
    name, rowid = row
    return Recipe(name, rowid)

  @staticmethod
  def list(cursor):
    cursor.execute("SELECT name, rowid FROM Recipes;")
    for row in cursor:
      yield Recipe.__from_row(row)

  @staticmethod
  def fetch(cursor, i):
    cursor.execute("SELECT name, rowid FROM Recipes WHERE rowid = ?;", (i,))
    row = cursor.fetchone()
    if row is None:
      return None
    return Recipe.__from_row(row)

  @staticmethod
  def save(cursor, recipe):
    if recipe.rowid is None:
      cursor.execute("INSERT INTO Recipes (name) VALUES (?);", (recipe.name,))
      return Recipe(recipe.name, cursor.lastrowid)
    else:
      cursor.execute("UPDATE Recipes SET name = ? WHERE rowid = ?;", (recipe.name, recipe.rowid))
      return recipe

  @staticmethod
  def ingredients(cursor, recipe_id):
    cursor.execute("""SELECT name, category, foodid
                      FROM RecipeContents
                      JOIN FoodItems ON FoodItems.rowid = RecipeContents.foodid
                      WHERE recipe_id = ?""", (recipe_id,))
    for row in cursor:
      yield Food._Food__from_row(row)

  @staticmethod
  def contains(cursor, recipe_id, foodid):
    cursor.execute("SELECT EXISTS(SELECT 1 FROM RecipeContents WHERE recipe_id = ? AND foodid = ?);", (recipe_id, foodid,))
    return cursor.fetchone()[0]

  @staticmethod
  def add_ingredient(cursor, recipe_id, foodid):
    cursor.execute("INSERT INTO RecipeContents (recipe_id, foodid) VALUES (?, ?);", (recipe_id, foodid))

  @staticmethod
  def remove_ingredient(cursor, recipe_id, foodid):
    cursor.execute("DELETE FROM RecipeContents WHERE recipe_id = ? AND foodid = ?;", (recipe_id, foodid))


