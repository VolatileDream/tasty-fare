from models.food import Food
from models.category import Category
from models.recipe import Recipe
from models.db import database

import unittest

class RecipeTests(unittest.TestCase):
  def s(self):
    db = database()
    cursor = db.cursor()
    Category.setup(cursor)
    Food.setup(cursor)
    Recipe.setup(cursor)

    return (db, cursor)

  def test_create(self):
    db, cursor = self.s()

    bread = Recipe.save(cursor, Recipe("Rye Bread"))
    self.assertEqual(Recipe.fetch(cursor, bread.rowid), bread)

  def test_not_found(self):
    db, cursor = self.s()

    self.assertIsNone(Recipe.fetch(cursor, 3))

  def test_list(self):
    db, cursor = self.s()

    bread = Recipe.save(cursor, Recipe("bread"))
    cake = Recipe.save(cursor, Recipe("cake"))

    recipes = set(Recipe.list(cursor))
    self.assertEqual(set([bread, cake]), recipes)

  def test_manage_ingredients(self):
    db, cursor = self.s()

    bread = Recipe.save(cursor, Recipe("bread"))
    flour = Food.save(cursor, Food("flour"))

    self.assertFalse(Recipe.contains(cursor, bread.rowid, flour.rowid))

    Recipe.add_ingredient(cursor, bread.rowid, flour.rowid)

    self.assertTrue(Recipe.contains(cursor, bread.rowid, flour.rowid))

    Recipe.remove_ingredient(cursor, bread.rowid, flour.rowid)

    self.assertFalse(Recipe.contains(cursor, bread.rowid, flour.rowid))

