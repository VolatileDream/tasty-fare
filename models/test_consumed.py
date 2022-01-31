from models.category import Category
from models.food import Food
from models.consumed import ConsumedFood
from models.db import database

import unittest

class ConsumedFoodTests(unittest.TestCase):
  def setUp(self):
    self.db = database()
    self.cursor = self.db.cursor()
    Category.setup(self.cursor)
    Food.setup(self.cursor)
    ConsumedFood.setup(self.cursor)

  def test_setup(self):
    groceries = list(ConsumedFood.list(self.cursor))
    self.assertEqual([], groceries)

    self.assertFalse(ConsumedFood.contains(self.cursor, 3))

  def test_empty_remove(self):
    ConsumedFood.remove(self.cursor, 3)

  def test_add_remove(self):
    bread = Food.save(self.cursor, Food("Bread"))

    ConsumedFood.add(self.cursor, bread.rowid)

    self.assertTrue(ConsumedFood.contains(self.cursor, bread.rowid))
    self.assertEqual(set([bread]), set(ConsumedFood.list(self.cursor)))

    ConsumedFood.remove(self.cursor, bread.rowid)

    self.assertFalse(ConsumedFood.contains(self.cursor, bread.rowid))
    self.assertEqual(set(), set(ConsumedFood.list(self.cursor)))
