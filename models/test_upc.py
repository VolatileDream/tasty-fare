from models.food import Food
from models.category import Category
from models.upc import ProductCodeMapping
from models.db import database

import sqlite3
import unittest

class ProductCodeMappingTests(unittest.TestCase):
  def setUp(self):
    self.db = database()
    self.cursor = self.db.cursor()
    Category.setup(self.cursor)
    Food.setup(self.cursor)
    ProductCodeMapping.setup(self.cursor)

  def test_setup_creates_garbage(self):
    upcs = list(ProductCodeMapping.list(self.cursor))
    self.assertEqual([], upcs)

  def test_add_no_food(self):
    with self.assertRaises(sqlite3.IntegrityError):
      ProductCodeMapping.update_map(self.cursor, 123, 456)

  def test_add(self):
    bread = Food.save(self.cursor, Food("bread"))
    
    ProductCodeMapping.update_map(self.cursor, 123, bread.rowid)

    upcs = list(ProductCodeMapping.list(self.cursor))
    self.assertEqual([ProductCodeMapping(123, bread.rowid)], upcs)

  def test_update(self):
    bread = Food.save(self.cursor, Food("bread"))
    milk = Food.save(self.cursor, Food("milk"))
    
    ProductCodeMapping.update_map(self.cursor, 123, bread.rowid)
    ProductCodeMapping.update_map(self.cursor, 123, milk.rowid)

    upcs = list(ProductCodeMapping.list(self.cursor))
    self.assertEqual([ProductCodeMapping(123, milk.rowid)], upcs)

  def test_lookup(self):
    bread = Food.save(self.cursor, Food("bread"))
    
    ProductCodeMapping.update_map(self.cursor, 123, bread.rowid)

    mapped = ProductCodeMapping.lookup(self.cursor, 123)
    self.assertEqual(mapped, ProductCodeMapping(123, bread.rowid))
