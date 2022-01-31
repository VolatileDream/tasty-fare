from models.food import Food
from models.category import Category
from models.db import database

import unittest

class FoodTests(unittest.TestCase):
  def test_setup_creates_garbage(self):
    db = database()
    cursor = db.cursor()
    Category.setup(cursor)
    Food.setup(cursor)

    cats = list(Food.list(cursor))
    self.assertEqual([], cats)

  def test_create(self):
    db = database()
    cursor = db.cursor()
    Category.setup(cursor)
    Food.setup(cursor)

    bread = Food.save(cursor, Food("Bread"))
    self.assertEqual(Food.fetch(cursor, bread.rowid), bread)

  def test_not_found(self):
    db = database()
    cursor = db.cursor()
    Category.setup(cursor)
    Food.setup(cursor)

    self.assertIsNone(Food.fetch(cursor, 3))

  def test_list(self):
    db = database()
    cursor = db.cursor()
    Category.setup(cursor)
    Food.setup(cursor)

    bread = Food.save(cursor, Food("Bread"))
    milk = Food.save(cursor, Food("Milk"))
    cereal = Food.save(cursor, Food("Cereal"))

    cats = set(Food.list(cursor))
    self.assertEqual(set([bread, milk, cereal]), cats)
