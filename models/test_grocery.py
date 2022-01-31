from models.category import Category
from models.food import Food
from models.grocery import Grocery
from models.db import database

import unittest

class GroceryTests(unittest.TestCase):
  def setUp(self):
    self.db = database()
    self.cursor = self.db.cursor()
    Category.setup(self.cursor)
    Food.setup(self.cursor)
    Grocery.setup(self.cursor)

  def test_setup(self):
    groceries = list(Grocery.list(self.cursor))
    self.assertEqual([], groceries)

    self.assertFalse(Grocery.contains(self.cursor, 3))

  def test_empty_remove(self):
    Grocery.remove(self.cursor, 3)

  def test_add_remove(self):
    bread = Food.save(self.cursor, Food("Bread"))

    Grocery.add(self.cursor, bread.rowid)

    self.assertTrue(Grocery.contains(self.cursor, bread.rowid))
    self.assertEqual(set([bread]), set(Grocery.list(self.cursor)))

    Grocery.remove(self.cursor, bread.rowid)

    self.assertFalse(Grocery.contains(self.cursor, bread.rowid))
    self.assertEqual(set(), set(Grocery.list(self.cursor)))
